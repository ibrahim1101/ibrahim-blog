import hashlib,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scheduler import submit_pr
class ScheduledPRTests(unittest.TestCase):
 def test_one_attempt_and_no_public_opt_in_by_default(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'drafts').mkdir();(root/'data/jobs').mkdir(parents=True);files=[]
   for name,body in [('story.md','# An example title\n\nA sample article introduction.\n'),('story.research.json','{}'),('story.quality.json','{}')]:
    b=body.encode();(root/'drafts'/name).write_bytes(b);files.append({'name':name,'sha256':hashlib.sha256(b).hexdigest()})
   (root/'data/jobs/2026-10-26.json').write_text(json.dumps({'job_id':'2026-10-26','files':files}));db=sqlite3.connect(':memory:');db.execute('CREATE TABLE pr_jobs(day TEXT PRIMARY KEY,state TEXT,updated TEXT,detail TEXT)')
   cfg={'automatic_draft_pr':True,'allow_public_draft_pr':False}
   with patch('scheduler.subprocess.run',return_value=SimpleNamespace(returncode=0,stdout='Draft PR: example',stderr='')) as call:
    submit_pr(db,root,'2026-10-26','cyber',cfg);submit_pr(db,root,'2026-10-26','cyber',cfg)
    self.assertEqual(call.call_count,1);self.assertNotIn('--allow-public',call.call_args.args[0]);self.assertEqual(db.execute('SELECT state FROM pr_jobs').fetchone()[0],'created')
 def test_disabled_never_creates_pr(self):
  db=sqlite3.connect(':memory:');db.execute('CREATE TABLE pr_jobs(day TEXT PRIMARY KEY,state TEXT,updated TEXT,detail TEXT)')
  with patch('scheduler.subprocess.run') as call:submit_pr(db,Path('/none'),'2026-10-26','cyber',{});call.assert_not_called()
if __name__=='__main__':unittest.main()

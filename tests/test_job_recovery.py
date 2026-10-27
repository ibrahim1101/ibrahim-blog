import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scheduler import completed_job
class RecoveryTests(unittest.TestCase):
 def test_reconcile_only_complete_and_unchanged_outputs(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'data/jobs').mkdir(parents=True);(root/'drafts').mkdir(); files=[]
   for name in ['story.md','story.research.json','story.quality.json']:
    content=name.encode();(root/'drafts'/name).write_bytes(content);files.append({'name':name,'sha256':hashlib.sha256(content).hexdigest()})
   marker=root/'data/jobs/2026-10-26.json';marker.write_text(json.dumps({'job_id':'2026-10-26','files':files}))
   self.assertTrue(completed_job(root,'2026-10-26'))
   (root/'drafts/story.md').write_text('changed');self.assertFalse(completed_job(root,'2026-10-26'))
   files[0]['name']='../outside';marker.write_text(json.dumps({'job_id':'2026-10-26','files':files}));self.assertFalse(completed_job(root,'2026-10-26'))
if __name__=='__main__':unittest.main()

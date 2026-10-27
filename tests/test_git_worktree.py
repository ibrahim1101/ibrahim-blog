import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import create_review_pr as pr
import editor
class GitWorktreeTest(unittest.TestCase):
 def test_separate_worktree_excludes_private_artifacts(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'repo';root.mkdir()
   def git(*args):return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True)
   git('init','-b','main');git('config','user.name','Test');git('config','user.email','test@example.invalid')
   (root/'.gitignore').write_text('drafts/\ndata/\n');(root/'README.md').write_text('test')
   git('add','.');git('commit','-m','initial');git('remote','add','origin','https://github.com/example/test.git');git('update-ref','refs/remotes/origin/main','HEAD')
   drafts=root/'drafts';drafts.mkdir();p=drafts/'story.md';p.write_text('# Draft\n\nFixture report text.\n')
   p.with_suffix('.research.json').write_text(json.dumps({'sources':[{'title':'Source','url':'https://example.com/source'}]}))
   p.with_suffix('.quality.json').write_text('{}'); calls=[]
   def runner(*args,capture=False,cwd=None):
    calls.append(args)
    if args[:3]==('gh','repo','view'):return SimpleNamespace(stdout='{"isPrivate":true}')
    if args[:3]==('gh','pr','create'):return SimpleNamespace(stdout='https://example.invalid/pr/1')
    if args[:2] in (('git','fetch'),('git','push')):return SimpleNamespace(stdout='')
    return subprocess.run(list(args),cwd=cwd or root,check=True,text=True,capture_output=True)
   with patch.object(pr,'ROOT',root),patch.object(editor,'DRAFTS',drafts),patch.object(pr,'run',side_effect=runner):
    result=pr.create('story.md','Headline','Description','cyber','2026-10-27','example/test',job_id='2026-10-27')
   self.assertTrue(result.endswith('/pr/1'));self.assertEqual(git('branch','--show-current').stdout.strip(),'main')
   names=git('diff','--name-only','main','review/scheduled-2026-10-27').stdout.splitlines()
   self.assertEqual(names,['website/src/content/articles/story.md']);self.assertNotIn('merge',[x for call in calls for x in call])
if __name__=='__main__':unittest.main()

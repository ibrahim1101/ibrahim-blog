import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import create_review_pr as pr
class PRWorkflowTests(unittest.TestCase):
 def test_public_repo_fails_closed_before_branch_or_push(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'draft.md';p.write_text('draft'); calls=[]
   def fake(*args,capture=False):
    calls.append(args)
    if args[:3]==('git','remote','get-url'):out='https://github.com/ibrahim1101/ibrahim-blog.git'
    elif args[:3]==('git','branch','--show-current'):out='main'
    elif args[:3]==('gh','repo','view'):out=json.dumps({'isPrivate':False})
    else:out=''
    return SimpleNamespace(stdout=out)
   with patch.object(pr.editor,'selected',return_value=p),patch.object(pr.editor,'artifacts'),patch.object(pr,'run',side_effect=fake):
    with self.assertRaisesRegex(ValueError,'Public PRs'):pr.create('draft.md','Title','Description','cyber','2026-10-27','ibrahim1101/ibrahim-blog')
   self.assertFalse(any(c[:2] in (('git','switch'),('git','push')) for c in calls))
 def test_private_repo_creates_draft_without_merging(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);p=root/'draft.md';p.write_text('draft');out=root/'website/article.md';out.parent.mkdir();out.write_text('article');calls=[]
   def fake(*args,capture=False):
    calls.append(args)
    if args[:3]==('git','remote','get-url'):text='https://github.com/ibrahim1101/ibrahim-blog.git'
    elif args[:3]==('git','branch','--show-current'):text='main'
    elif args[:3]==('gh','repo','view'):text=json.dumps({'isPrivate':True})
    elif args[:3]==('gh','pr','create'):text='https://github.example/pr/1'
    else:text=''
    return SimpleNamespace(stdout=text)
   with patch.object(pr,'ROOT',root),patch.object(pr.editor,'selected',return_value=p),patch.object(pr.editor,'artifacts'),patch.object(pr.editor,'stage',return_value=out),patch.object(pr,'run',side_effect=fake):
    self.assertTrue(pr.create('draft.md','Title','Description','cyber','2026-10-27','ibrahim1101/ibrahim-blog').endswith('/pr/1'))
   self.assertTrue(any(c[:3]==('gh','pr','create') and '--draft' in c for c in calls))
   self.assertFalse(any('merge' in c for c in calls))
if __name__=='__main__':unittest.main()

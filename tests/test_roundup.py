import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import editor,roundup
class RoundupTests(unittest.TestCase):
 def test_roundup_remains_review_required(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);drafts=root/'drafts';drafts.mkdir()
   for n in ('one','two'):
    p=drafts/(n+'.md');p.write_text('# '+n)
    p.with_suffix('.research.json').write_text(json.dumps({'sources':[{'title':n,'url':f'https://{n}.example/story','text':'The organization released a fictional update.'}]}))
    p.with_suffix('.quality.json').write_text('{}')
   with patch.object(roundup,'ROOT',root),patch.object(editor,'DRAFTS',drafts),patch.object(roundup.blog,'ask',side_effect=['Fictional notes','# Weekly roundup\n\nThe organization released a fictional update.']):out=roundup.prepare(['one.md','two.md'],'ai')
   report=json.loads(out.with_suffix('.quality.json').read_text());self.assertFalse(report['publication_allowed']);self.assertEqual(report['status'],'REVIEW_REQUIRED')
if __name__=='__main__':unittest.main()

import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import blog,editor
class EditorActions(unittest.TestCase):
 def test_research_creates_new_packet_and_preserves_original(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);p=root/'draft.md';p.write_text('original draft');research=p.with_suffix('.research.json');research.write_text(json.dumps({'primary':'https://example.com/story','sources':[{'url':'https://example.com/story','title':'Story'}]}));p.with_suffix('.quality.json').write_text('{}');before=research.read_bytes()
   source='A factual source passage. '*20
   with patch.object(blog,'get_page',return_value=(source,'https://example.com/story',[])),patch.object(blog,'gather_sources',side_effect=lambda first,c:[first]):
    new=editor.research_more(p)
   self.assertTrue(new.exists());self.assertEqual(research.read_bytes(),before);self.assertEqual(p.read_text(),'original draft');self.assertTrue(json.loads(new.read_text())['review_required'])
if __name__=='__main__':unittest.main()

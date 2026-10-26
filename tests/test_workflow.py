import json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import editor, editorial
class WorkflowTests(unittest.TestCase):
 def test_staging_never_approves_and_requires_evidence(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); drafts=root/'drafts'; drafts.mkdir(); pub=root/'site'; draft=drafts/'candidate.md'
   draft.write_text('# Draft headline\n\nThe vendor reported an incident.',encoding='utf8')
   draft.with_suffix('.research.json').write_text(json.dumps({'sources':[{'title':'Vendor','url':'https://example.org/advisory'}]}))
   draft.with_suffix('.quality.json').write_text(json.dumps({'publication_allowed':False,'status':'REVIEW_REQUIRED'}))
   with patch.object(editor,'DRAFTS',drafts),patch.object(editor,'PUBLIC',pub):
    out=editor.stage(editor.selected('candidate.md'),'Reviewed headline','A concise description','cyber','2026-10-27')
    self.assertTrue(out.exists()); self.assertIn('REVIEW_REQUIRED',draft.with_suffix('.quality.json').read_text())
    with self.assertRaises(ValueError): editor.stage(draft,'A','B','cyber','2026-10-27')
    with self.assertRaises(ValueError): editor.selected('../candidate.md')
 def test_gate_never_marks_approved(self):
  d=[{'url':'https://example.org/report','text':'The vendor said the data may have been exposed.'}]
  result=editorial.quality_report('# Report\n\nThe vendor said the data was exposed.',d,editorial.source_provenance(d),[])
  self.assertFalse(result['publication_allowed']);self.assertEqual(result['status'],'REVIEW_REQUIRED')
if __name__=='__main__': unittest.main()

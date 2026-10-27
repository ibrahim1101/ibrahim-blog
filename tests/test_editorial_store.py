import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial_store import connect,state,transition
class EditorialStoreTests(unittest.TestCase):
 def test_audited_decision_invalidated_by_edits(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'draft.md';p.write_text('first');db=connect(Path(t)/'review.sqlite')
   self.assertEqual(state(db,p),'REVIEW_REQUIRED')
   transition(db,p,'REVIEWED','Editor','Checked against sources')
   self.assertEqual(state(db,p),'REVIEWED');p.with_suffix('.research.json').write_text('new evidence');self.assertEqual(state(db,p),'REVIEW_REQUIRED')
   transition(db,p,'REVIEWED','Editor','Rechecked evidence');p.write_text('edited');self.assertEqual(state(db,p),'REVIEW_REQUIRED')
   self.assertEqual(db.execute('select count(*) from review_events').fetchone()[0],2)
   with self.assertRaises(ValueError):transition(db,p,'PUBLISHED','Editor','bypass')
   db.close()
 def test_reviewer_note_required(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'draft.md';p.write_text('test');db=connect(Path(t)/'r.sqlite')
   with self.assertRaises(ValueError):transition(db,p,'REVIEWED','','')
   db.close()
if __name__=='__main__':unittest.main()

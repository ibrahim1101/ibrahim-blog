import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from candidates import connect,add
class CandidateTests(unittest.TestCase):
 def test_collect_is_idempotent_and_preserves_rejection(self):
  with tempfile.TemporaryDirectory() as tmp:
   db=connect(Path(tmp)/'c.sqlite');item={'url':'https://example.com/story','title':'Example story','published':'2026-01-01'}
   self.assertEqual(add(db,'cyber',[item,item]),1);db.execute("UPDATE candidates SET state='REJECTED'");db.commit();self.assertEqual(add(db,'cyber',[item]),0);self.assertEqual(db.execute('SELECT state FROM candidates').fetchone()[0],'REJECTED');db.close()
if __name__=='__main__':unittest.main()

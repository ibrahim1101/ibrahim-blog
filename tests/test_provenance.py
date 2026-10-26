import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial import source_provenance
class Provenance(unittest.TestCase):
 def test_credit_is_recorded_and_missing_credit_not_independent(self):
  first={'url':'https://bleepingcomputer.com/story','text':'Some original report.'}
  second={'url':'https://another.example/story','text':'As reported by BleepingComputer, the company said it happened.'}
  p=source_provenance([first,second]);self.assertEqual(p[1]['explicitly_attributes_to'],['bleepingcomputer.com']);self.assertTrue(p[1]['attribution_evidence']);self.assertEqual(p[0]['provenance'],'unverified')
 def test_shared_passage_is_warning_not_independence(self):
  long='The organization announced that an incident affected multiple systems and the investigation remains ongoing according to its published advisory on Tuesday morning. '
  p=source_provenance([{'url':'https://one.example/a','text':long*3},{'url':'https://two.example/a','text':long*3}])
  self.assertTrue(p[0]['potential_syndication']);self.assertEqual(p[0]['provenance'],'unverified')
if __name__=='__main__':unittest.main()

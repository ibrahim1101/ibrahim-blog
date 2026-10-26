import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from review import review_article
class Claims(unittest.TestCase):
 def test_heading_and_opening_are_separate_claims(self):
  items=review_article('# Vendor confirms 50 affected users\n\nThe vendor says 50 users may have been affected.',[{'text':'The vendor says 50 users may have been affected.'}])
  self.assertEqual(len(items),2); self.assertTrue(any('certainty' in x for x in items[0]['flags']))
 def test_quote_and_number_warning(self):
  items=review_article('The vendor said "all users are now safe" and 500 users were affected.',[{'text':'The vendor said 50 users were affected.'}])
  self.assertTrue(any('quotation' in x for x in items[0]['flags'])); self.assertTrue(any('numbers' in x for x in items[0]['flags']))
 def test_candidate_is_not_automatically_supported(self):
  items=review_article('The vendor said 50 users were affected.',[{'text':'The vendor said 50 users were affected.'}]);self.assertEqual(items[0]['status'],'UNVERIFIED');self.assertFalse(items[0]['human_verified'])
if __name__=='__main__':unittest.main()

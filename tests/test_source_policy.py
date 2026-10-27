import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import blog
class Policies(unittest.TestCase):
 def test_policy_matches_hostname_boundaries_and_disabled_source(self):
  policies={'example.com':{'enabled':False,'role':'secondary','priority':80}}
  with patch.dict(blog.CONFIG,{'source_policies':policies,'official_source_hosts':[]}):
   self.assertFalse(blog.source_policy('https://news.example.com/story')['enabled'])
   self.assertTrue(blog.source_policy('https://example.com.attacker.invalid/story')['enabled'])
   self.assertEqual(blog.source_policy('https://news.example.com/story')['priority'],80)
 def test_disabled_source_is_blocked_before_crawl(self):
  with patch.dict(blog.CONFIG,{'source_policies':{'example.com':{'enabled':False}},'official_source_hosts':[]}):
   with patch.object(blog,'CRAWL_POLICY') as policy:
    with self.assertRaises(ValueError):blog.check_article_request('https://example.com/story')
    policy.assert_not_called()
 def test_invalid_role_is_not_treated_as_verified(self):
  with patch.dict(blog.CONFIG,{'source_policies':{'example.com':{'role':'verified_primary'}},'official_source_hosts':[]}):
   self.assertEqual(blog.source_policy('https://example.com/story')['role'],'unverified')
if __name__=='__main__':unittest.main()

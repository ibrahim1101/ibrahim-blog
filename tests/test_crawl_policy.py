import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from crawl_policy import CrawlPolicy
class CrawlTests(unittest.TestCase):
 def test_robots_denial_and_cache(self):
  calls=[]
  def fetch(url,**kwargs):calls.append(url);return (b'User-agent: *\nDisallow: /private\n',url,'text/plain')
  p=CrawlPolicy(fetch,interval=0);p('https://example.com/public')
  with self.assertRaises(ValueError):p('https://example.com/private')
  self.assertEqual(len(calls),1)
 def test_unknown_failure_is_not_permission(self):
  def fetch(*a,**kw):raise ValueError('HTTP 403')
  with self.assertRaises(ValueError):CrawlPolicy(fetch,interval=0)('https://example.com/x')
 def test_missing_robots_is_allowed(self):
  def fetch(*a,**kw):raise ValueError('HTTP 404')
  CrawlPolicy(fetch,interval=0)('https://example.com/x')
if __name__=='__main__':unittest.main()

"""Conservative robots policy and process-local per-host pacing for article fetches."""
import time
from urllib.parse import urlsplit,urlunsplit
from urllib.robotparser import RobotFileParser

class CrawlPolicy:
 def __init__(self,fetcher,interval=1.0,ttl=3600):self.fetcher=fetcher;self.interval=interval;self.ttl=ttl;self.cache={};self.last={}
 def wait(self,origin):
  now=time.monotonic();delay=self.interval-(now-self.last.get(origin,-1e30))
  if delay>0:time.sleep(delay)
  self.last[origin]=time.monotonic()
 def __call__(self,url):
  u=urlsplit(url);origin=urlunsplit((u.scheme,u.netloc,'','',''));now=time.monotonic();entry=self.cache.get(origin)
  if not entry or now-entry[0]>self.ttl:
   self.wait(origin)
   try:
    raw,_,ctype=self.fetcher(origin+'/robots.txt',limit=250000,redirects=0)
    if 'text/html' in ctype.lower():raise ValueError('robots response was HTML')
    parser=RobotFileParser();parser.parse(raw.decode('utf8',errors='replace').splitlines());entry=(time.monotonic(),parser)
   except (OSError,ValueError) as exc:
    # Missing robots.txt permits crawling; access failures or redirects are not permission.
    entry=(time.monotonic(),True if str(exc)=='HTTP 404' else False)
   self.cache[origin]=entry
  rules=entry[1]
  allowed=rules if isinstance(rules,bool) else rules.can_fetch('IbrahimBlogResearch',url)
  if not allowed:raise ValueError('robots.txt denies or could not be checked')
  self.wait(origin)

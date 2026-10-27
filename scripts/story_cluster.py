"""Conservative headline similarity for review grouping, never source corroboration."""
import re
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
STOP={'the','and','for','with','from','after','about','says','said','new','report','reports','this','that','into','over','its','their','first'}
def canonical_url(url):
 u=urlsplit(url); query=urlencode([(k,v) for k,v in parse_qsl(u.query,keep_blank_values=True) if not (k.lower().startswith('utm_') or k.lower() in {'fbclid','gclid','mc_cid','mc_eid'})])
 return urlunsplit((u.scheme.lower(),u.netloc.lower(),u.path.rstrip('/') or '/',query,''))
def words(title):
 return {w for w in re.findall(r'[a-z0-9]+',title.lower()) if len(w)>2 and w not in STOP}
def similar(a,b):
 aa,bb=words(a),words(b)
 if len(aa)<4 or len(bb)<4:return False
 # Distinct figures and CVE IDs must not be silently clustered.
 numbers=lambda t:set(re.findall(r'(?i)CVE-\d{4}-\d+|\b\d+(?:\.\d+)*\b',t))
 if numbers(a)!=numbers(b):return False
 overlap=len(aa & bb)/len(aa | bb)
 ratio=SequenceMatcher(None,' '.join(sorted(aa)),' '.join(sorted(bb))).ratio()
 return overlap>=.65 and ratio>=.8

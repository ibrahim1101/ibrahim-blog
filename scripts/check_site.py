"""Check emitted internal HTML links and basic page metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]/'website'/'dist'
class Parser(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.title=False; self.description=False; self.canonical=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href'): self.links.append(d['href'])
        if tag=='title': self.title=True
        if tag=='meta' and d.get('name')=='description': self.description=True
        if tag=='link' and d.get('rel')=='canonical': self.canonical=True
errors=[]
for page in ROOT.rglob('*.html'):
    p=Parser();p.feed(page.read_text(encoding='utf-8'))
    if not all([p.title,p.description,p.canonical]): errors.append(f'{page}: missing metadata')
    for link in p.links:
        u=urlsplit(link)
        if not u.path.startswith('/') or u.netloc: continue
        target=ROOT/unquote(u.path).lstrip('/')
        if not target.exists() and not (target/'index.html').exists(): errors.append(f'{page}: missing {link}')
if errors: raise SystemExit('\n'.join(errors))
print('Static pages: internal links and metadata OK')

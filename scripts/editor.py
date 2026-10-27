#!/usr/bin/env python3
"""Local editorial handoff. Never publishes, merges, or grants approval."""
import argparse
from contextlib import closing
import datetime as dt
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from editorial_store import connect, state, transition

ROOT=Path(__file__).resolve().parents[1]
DRAFTS=(ROOT/'drafts').resolve()
PUBLIC=ROOT/'website'/'src'/'content'/'articles'
CATEGORIES={'ai','cyber','gaming','dev'}

def selected(name):
    p=(DRAFTS/name).resolve()
    if p.parent!=DRAFTS or p.suffix!='.md' or not p.is_file(): raise ValueError('Select an existing draft filename from drafts/')
    return p

def artifacts(p):
    prefix=p.with_suffix('')
    research=prefix.with_suffix('.research.json'); quality=prefix.with_suffix('.quality.json')
    if not research.is_file() or not quality.is_file(): raise ValueError('Matching evidence and quality reports required')
    return json.loads(research.read_text(encoding='utf-8')),json.loads(quality.read_text(encoding='utf-8'))

def stage(p,title,description,category,date):
    evidence,quality=artifacts(p)
    if category not in CATEGORIES or not title.strip() or not description.strip(): raise ValueError('Valid title, description and category required')
    dt.date.fromisoformat(date)
    sources=evidence.get('sources',[])
    if not sources or not all(isinstance(x.get('url'),str) and x['url'].startswith(('https://','http://')) for x in sources): raise ValueError('Source URLs required')
    body=p.read_text(encoding='utf-8')
    body=re.sub(r'^\s*<!--.*?-->\s*','',body,flags=re.S)
    body=re.sub(r'^\s*#\s+[^\n]+\n','',body,count=1)
    slug=re.sub(r'[^a-z0-9]+','-',p.stem.lower()).strip('-')
    PUBLIC.mkdir(parents=True,exist_ok=True); output=PUBLIC/(slug+'.md')
    if output.exists(): raise ValueError('Publication file already exists; edit it explicitly')
    # JSON strings are also valid YAML scalars; prevent frontmatter injection.
    front=['---','title: '+json.dumps(title,ensure_ascii=False),'description: '+json.dumps(description,ensure_ascii=False),'category: '+category,'author: "Shaik Ibrahim"','published: '+json.dumps(date),'disclosure: "AI tools assisted preparation. Editorial review is required before publication."','sources:']
    for item in sources: front += ['  - title: '+json.dumps(item.get('title') or item['url'],ensure_ascii=False),'    url: '+json.dumps(item['url'],ensure_ascii=False)]
    output.write_text('\n'.join(front+['---','',body.strip(),'']),encoding='utf-8')
    return output

def research_more(path):
    """Save a fresh evidence packet; never modify the original draft or evidence."""
    import blog
    from editorial import source_provenance
    evidence,_=artifacts(path)
    url=evidence.get('primary') or (evidence.get('sources') or [{}])[0].get('url')
    if not isinstance(url,str) or not blog.valid_public_url(url): raise ValueError('No valid original source URL')
    original=next((x for x in evidence.get('sources',[]) if isinstance(x,dict) and x.get('url')==url),{})
    title=original.get('title') or path.stem
    body,final,links=blog.get_page(url)
    first={'title':title,'url':final,'published':'unknown','feed':'editorial-refresh','text':body,'outbound_links':links}
    documents=blog.gather_sources(first,[])
    first.pop('outbound_links',None)
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    for d in documents:d['retrieved_at']=stamp
    output=path.parent/(path.stem+'.research-extension-'+uuid.uuid4().hex[:12]+'.json')
    blog.atomic_text(output,json.dumps({'generated_at':stamp,'original_draft':path.name,'sources':documents,'source_provenance':source_provenance(documents),'review_required':True},indent=2,ensure_ascii=False))
    return output

def regenerate(path):
    """Generate a new draft using the original source; preserves existing artifacts."""
    import blog
    evidence,_=artifacts(path)
    url=evidence.get('primary') or (evidence.get('sources') or [{}])[0].get('url')
    category=evidence.get('category')
    if not isinstance(url,str) or not blog.valid_public_url(url) or category not in CATEGORIES:raise ValueError('Original source or category is missing')
    title=next((x.get('title') for x in evidence.get('sources',[]) if isinstance(x,dict) and x.get('url')==url and x.get('title')),path.stem)
    return subprocess.run([sys.executable,str(ROOT/'scripts'/'blog.py'),'--category',category,'--url',url,'--title',title,'--force'],cwd=ROOT).returncode

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('list'); show=sub.add_parser('show'); show.add_argument('draft')
    decision=sub.add_parser('decision'); decision.add_argument('draft'); decision.add_argument('--state',choices=['REVIEW_REQUIRED','NEEDS_REVISION','REJECTED','REVIEWED'],required=True); decision.add_argument('--reviewer',required=True); decision.add_argument('--note',required=True)
    history=sub.add_parser('history'); history.add_argument('draft')
    research=sub.add_parser('research'); research.add_argument('draft')
    regen=sub.add_parser('regenerate'); regen.add_argument('draft')
    st=sub.add_parser('stage'); st.add_argument('draft'); st.add_argument('--title',required=True); st.add_argument('--description',required=True); st.add_argument('--category',choices=sorted(CATEGORIES),required=True); st.add_argument('--date',required=True)
    args=ap.parse_args()
    if args.cmd=='list':
        for p in sorted(DRAFTS.glob('*.md')): print(p.name)
    elif args.cmd=='show':
        p=selected(args.draft); evidence,quality=artifacts(p)
        print(p.read_text(encoding='utf-8'));print('\n--- QUALITY REPORT ---\n'+json.dumps(quality,indent=2,ensure_ascii=False));print('\n--- SOURCE EVIDENCE ---\n'+json.dumps(evidence.get('sources',[]),indent=2,ensure_ascii=False))
    elif args.cmd=='research':
        print('Additional research:',research_more(selected(args.draft)))
    elif args.cmd=='regenerate':
        return regenerate(selected(args.draft))
    elif args.cmd in ('decision','history'):
        p=selected(args.draft); artifacts(p); (ROOT/'data').mkdir(exist_ok=True)
        with closing(connect(ROOT/'data'/'editorial.sqlite3')) as db, db:
            if args.cmd=='history':
                print('Current:',state(db,p))
                for row in db.execute('SELECT at,prior_state,state,actor,note,content_sha256 FROM review_events WHERE draft=? ORDER BY id',(p.name,)):print(json.dumps(row,ensure_ascii=False))
            else:
                print('This is a local audit note, not authenticated GitHub approval or permission to publish.')
                if input('Type RECORD to continue: ').strip()!='RECORD':return 1
                print('Recorded:',transition(db,p,args.state,args.reviewer,args.note))
    else:
        print('This copies a draft into the website content directory. It is NOT approval. Use a review branch; never push directly to production.')
        if input('Type STAGE to continue: ').strip()!='STAGE': return 1
        print('Staged:',stage(selected(args.draft),args.title,args.description,args.category,args.date))
        print('Review every claim and edit the article. Open a draft PR; only a human may approve and merge.')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except (ValueError,OSError,json.JSONDecodeError) as e: sys.exit(str(e))

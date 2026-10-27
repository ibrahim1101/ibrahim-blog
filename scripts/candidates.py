#!/usr/bin/env python3
"""Local story queue. Discovery and generation never approve or publish content."""
import argparse,datetime as dt,hashlib,json,sqlite3,subprocess,sys
from pathlib import Path
import blog
from story_cluster import canonical_url, similar
ROOT=Path(__file__).resolve().parents[1]

def connect(path):
 db=sqlite3.connect(path)
 db.execute('CREATE TABLE IF NOT EXISTS candidates (id TEXT PRIMARY KEY, url TEXT UNIQUE NOT NULL, title TEXT NOT NULL, category TEXT NOT NULL, published TEXT NOT NULL, state TEXT NOT NULL, updated TEXT NOT NULL)')
 cols={row[1] for row in db.execute('PRAGMA table_info(candidates)')}
 if 'cluster_id' not in cols: db.execute('ALTER TABLE candidates ADD COLUMN cluster_id TEXT')
 db.commit();return db

def add(db,category,items):
 now=dt.datetime.now(dt.timezone.utc).isoformat();n=0
 with db:
  for item in items:
   url=canonical_url(item['url']);key=hashlib.sha256(url.encode()).hexdigest()[:16]
   existing=db.execute('SELECT id,title,cluster_id FROM candidates WHERE category=?',(category,)).fetchall()
   cluster=next(((row[2] or row[0]) for row in existing if similar(item['title'],row[1])),key)
   n+=db.execute('INSERT OR IGNORE INTO candidates(id,url,title,category,published,state,updated,cluster_id) VALUES (?,?,?,?,?,?,?,?)',(key,url,item['title'],category,item['published'],'DISCOVERED',now,cluster)).rowcount
 return n

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 get=sub.add_parser('collect');get.add_argument('--category',choices=blog.CONFIG['feeds'],required=True)
 sub.add_parser('list');reject=sub.add_parser('reject');reject.add_argument('id');generate=sub.add_parser('generate');generate.add_argument('id')
 args=p.parse_args();(ROOT/'data').mkdir(exist_ok=True)
 with connect(ROOT/'data'/'candidates.sqlite3') as db:
  if args.command=='collect': print('New candidates:',add(db,args.category,blog.collect(args.category)));return 0
  if args.command=='list':
   for row in db.execute('SELECT id,state,category,published,title,url,cluster_id FROM candidates ORDER BY published DESC'): print(json.dumps(row,ensure_ascii=False))
   return 0
  row=db.execute('SELECT url,title,category,state FROM candidates WHERE id=?',(args.id,)).fetchone()
  if not row: p.error('candidate not found')
  if row[3]!='DISCOVERED': p.error('candidate already processed or in progress')
  if args.command=='reject':
   with db:db.execute("UPDATE candidates SET state='REJECTED',updated=? WHERE id=? AND state='DISCOVERED'",(dt.datetime.now(dt.timezone.utc).isoformat(),args.id))
   return 0
  with db: changed=db.execute("UPDATE candidates SET state='GENERATING',updated=? WHERE id=? AND state='DISCOVERED'",(dt.datetime.now(dt.timezone.utc).isoformat(),args.id)).rowcount
  if not changed: p.error('candidate claimed by another process')
  try:rc=subprocess.run([sys.executable,str(ROOT/'scripts/blog.py'),'--category',row[2],'--url',row[0],'--title',row[1]],cwd=ROOT,timeout=7200).returncode
  except subprocess.TimeoutExpired:rc=1
  with db:db.execute('UPDATE candidates SET state=?,updated=? WHERE id=?',('DRAFTED' if rc==0 else 'FAILED',dt.datetime.now(dt.timezone.utc).isoformat(),args.id))
  return rc
if __name__=='__main__':raise SystemExit(main())

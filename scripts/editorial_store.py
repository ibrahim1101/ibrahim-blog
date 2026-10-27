"""Local audit of editorial decisions; not an authenticated publication approval."""
import datetime as dt
import hashlib
import sqlite3
from pathlib import Path

TRANSITIONS={'REVIEW_REQUIRED':{'NEEDS_REVISION','REJECTED','REVIEWED'},'NEEDS_REVISION':{'REVIEW_REQUIRED','REJECTED'},'REVIEWED':{'NEEDS_REVISION','REJECTED'},'REJECTED':{'REVIEW_REQUIRED'}}

def digest(path):
    path=Path(path); h=hashlib.sha256()
    # A review is tied to the article and both evidence artifacts.
    for p in (path,path.with_suffix('.research.json'),path.with_suffix('.quality.json')):
        data=p.read_bytes() if p.is_file() else b''
        h.update(p.name.encode());h.update(len(data).to_bytes(8,'big'));h.update(data)
    return h.hexdigest()

def connect(path):
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS reviews (draft TEXT PRIMARY KEY, state TEXT NOT NULL, content_sha256 TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS review_events (id INTEGER PRIMARY KEY, draft TEXT NOT NULL, at TEXT NOT NULL, prior_state TEXT, state TEXT NOT NULL, actor TEXT NOT NULL, note TEXT NOT NULL, content_sha256 TEXT NOT NULL)')
    return db

def state(db, path):
    p=Path(path);row=db.execute('SELECT state,content_sha256 FROM reviews WHERE draft=?',(p.name,)).fetchone()
    if not row:return 'REVIEW_REQUIRED'
    return row[0] if row[1]==digest(p) else 'REVIEW_REQUIRED'

def transition(db,path,target,actor,note):
    p=Path(path);current=state(db,p)
    if target not in TRANSITIONS.get(current,set()):raise ValueError(f'Invalid transition: {current} -> {target}')
    if not actor.strip() or not note.strip():raise ValueError('Reviewer and decision note required')
    checksum=digest(p);timestamp=dt.datetime.now(dt.timezone.utc).isoformat()
    with db:
        db.execute('INSERT INTO reviews VALUES (?,?,?) ON CONFLICT(draft) DO UPDATE SET state=excluded.state,content_sha256=excluded.content_sha256',(p.name,target,checksum))
        db.execute('INSERT INTO review_events(draft,at,prior_state,state,actor,note,content_sha256) VALUES (?,?,?,?,?,?,?)',(p.name,timestamp,current,target,actor.strip(),note.strip(),checksum))
    return target

#!/usr/bin/env python3
"""Persistent, draft-only scheduler. A failed or interrupted slot is never silently rerun."""
import argparse,datetime as dt,hashlib,json,sqlite3,subprocess,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
ZONE=ZoneInfo('Asia/Kolkata')

def slot(day):
    if day.weekday()==0:return 'ai'
    if day.weekday()==2:return 'cyber'
    if day.weekday()==4:return 'gaming' if day.isocalendar().week%2 else 'dev'
    return None

def due_days(today,days=7):
    return [(d,slot(d)) for n in range(days,-1,-1) if slot(d:=today-dt.timedelta(days=n))]

def completed_job(root,key):
    marker=root/'data'/'jobs'/f'{key}.json'
    try:
        manifest=json.loads(marker.read_text(encoding='utf8'))
        files=manifest['files']
        if manifest['job_id']!=key or not isinstance(files,list) or len(files)!=3:return False
        for item in files:
            name=item['name']
            if Path(name).name != name:return False
            data=(root/'drafts'/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=item['sha256']:return False
        return True
    except (OSError,ValueError,KeyError,TypeError):return False

def main():
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf8')).get('schedule',{})
    p=argparse.ArgumentParser();p.add_argument('--lookback-days',type=int,default=cfg.get('lookback_days',7));p.add_argument('--list',action='store_true');p.add_argument('--retry-failed',action='store_true',default=cfg.get('retry_failed',False)); args=p.parse_args()
    if not 0<=args.lookback_days<=30:p.error('lookback must be 0..30 days')
    try:
        zone=ZoneInfo(cfg.get('timezone','Asia/Kolkata')); draft_time=dt.time.fromisoformat(cfg.get('draft_time','10:00'))
        if draft_time.tzinfo: raise ValueError('time must not contain a timezone')
    except (ValueError,KeyError) as e:p.error('invalid schedule configuration: '+str(e))
    now=dt.datetime.now(zone);(ROOT/'data').mkdir(exist_ok=True)
    with sqlite3.connect(ROOT/'data'/'schedule.sqlite3',timeout=5) as db:
        db.execute('CREATE TABLE IF NOT EXISTS jobs (day TEXT PRIMARY KEY, category TEXT NOT NULL, state TEXT NOT NULL, updated TEXT NOT NULL)')
        for day,category in due_days(now.date(),args.lookback_days):
            key=day.isoformat();row=db.execute('SELECT state FROM jobs WHERE day=?',(key,)).fetchone()
            if row and row[0] in ('running','failed') and completed_job(ROOT,key):
                db.execute("UPDATE jobs SET state='drafted',updated=? WHERE day=?",(dt.datetime.now(dt.timezone.utc).isoformat(),key));db.commit();row=('drafted',)
            due=day<now.date() or now.time().replace(tzinfo=None)>=draft_time
            if args.list:print(key,category,(row[0] if row else ('pending' if due else 'not due')));continue
            if not due or (row and not (args.retry_failed and row[0]=='failed')):continue
            utc=dt.datetime.now(dt.timezone.utc).isoformat()
            if row:changed=db.execute("UPDATE jobs SET state='running',updated=? WHERE day=? AND state='failed'",(utc,key)).rowcount
            else:changed=db.execute('INSERT OR IGNORE INTO jobs VALUES (?,?,?,?)',(key,category,'running',utc)).rowcount
            db.commit()
            if not changed:continue
            print('Preparing',key,category,flush=True)
            try:result=subprocess.run([sys.executable,str(ROOT/'scripts'/'blog.py'),'--category',category,'--job-id',key],cwd=ROOT,timeout=7200);status='drafted' if result.returncode==0 else 'failed'
            except subprocess.TimeoutExpired: status='failed'
            db.execute('UPDATE jobs SET state=?,updated=? WHERE day=?',(status,dt.datetime.now(dt.timezone.utc).isoformat(),key));db.commit()
    return 0
if __name__=='__main__':raise SystemExit(main())

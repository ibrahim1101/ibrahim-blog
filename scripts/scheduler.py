#!/usr/bin/env python3
"""Persistent, draft-only scheduler. A failed or interrupted slot is never silently rerun."""
import argparse,datetime as dt,hashlib,json,re,sqlite3,subprocess,sys
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

def submit_pr(db,root,key,category,cfg,retry_failed=False):
    """One claimed attempt per job; ambiguous interruptions never auto-repeat."""
    if not cfg.get('automatic_draft_pr',False) or not completed_job(root,key):return
    prior=db.execute('SELECT state FROM pr_jobs WHERE day=?',(key,)).fetchone()
    if prior and not (retry_failed and prior[0]=='failed'):return
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    if prior:changed=db.execute("UPDATE pr_jobs SET state='running',updated=?,detail='' WHERE day=? AND state='failed'",(now,key)).rowcount
    else:changed=db.execute("INSERT OR IGNORE INTO pr_jobs VALUES (?,'running',?,'')",(key,now)).rowcount
    db.commit()
    if not changed:return
    manifest=json.loads((root/'data'/'jobs'/f'{key}.json').read_text(encoding='utf8'))
    draft_name=next((x['name'] for x in manifest['files'] if x['name'].endswith('.md')),None)
    if not draft_name:
        status='failed';detail='No draft in completed manifest.'
    else:
        text=(root/'drafts'/draft_name).read_text(encoding='utf8')
        heading=re.search(r'(?m)^#\s+(.+)$',text)
        title=heading.group(1).strip()[:160] if heading else ''
        paragraphs=[x.strip() for x in text.splitlines() if x.strip() and not x.lstrip().startswith(('#','<!--','-','['))]
        description=re.sub(r'\s+',' ',paragraphs[0])[:200] if paragraphs else ''
        if not title or not description:status='failed';detail='Draft title or description missing.'
        else:
            cmd=[sys.executable,str(root/'scripts'/'create_review_pr.py'),draft_name,'--title',title,'--description',description,'--category',category,'--date',key,'--repo',cfg.get('repository','ibrahim1101/ibrahim-blog'),'--job-id',key]
            if cfg.get('allow_public_draft_pr',False):cmd.append('--allow-public')
            try:
                result=subprocess.run(cmd,cwd=root,timeout=300,capture_output=True,text=True)
                status='created' if result.returncode==0 else 'failed'
                detail=(result.stdout if result.returncode==0 else result.stderr)[-2000:]
            except (OSError,subprocess.TimeoutExpired) as exc:status='failed';detail=str(exc)
    db.execute('UPDATE pr_jobs SET state=?,updated=?,detail=? WHERE day=?',(status,dt.datetime.now(dt.timezone.utc).isoformat(),detail,key));db.commit()
    print('Draft PR:',key,status,detail,flush=True)

def main():
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf8')).get('schedule',{})
    p=argparse.ArgumentParser();p.add_argument('--lookback-days',type=int,default=cfg.get('lookback_days',7));p.add_argument('--list',action='store_true');p.add_argument('--retry-failed',action='store_true',default=cfg.get('retry_failed',False));p.add_argument('--retry-pr-failed',action='store_true'); args=p.parse_args()
    if not 0<=args.lookback_days<=30:p.error('lookback must be 0..30 days')
    try:
        zone=ZoneInfo(cfg.get('timezone','Asia/Kolkata')); draft_time=dt.time.fromisoformat(cfg.get('draft_time','10:00'))
        if draft_time.tzinfo: raise ValueError('time must not contain a timezone')
    except (ValueError,KeyError) as e:p.error('invalid schedule configuration: '+str(e))
    now=dt.datetime.now(zone);(ROOT/'data').mkdir(exist_ok=True)
    with sqlite3.connect(ROOT/'data'/'schedule.sqlite3',timeout=5) as db:
        db.execute('CREATE TABLE IF NOT EXISTS jobs (day TEXT PRIMARY KEY, category TEXT NOT NULL, state TEXT NOT NULL, updated TEXT NOT NULL)')
        db.execute("CREATE TABLE IF NOT EXISTS pr_jobs (day TEXT PRIMARY KEY, state TEXT NOT NULL, updated TEXT NOT NULL, detail TEXT NOT NULL)")
        for day,category in due_days(now.date(),args.lookback_days):
            key=day.isoformat();row=db.execute('SELECT state FROM jobs WHERE day=?',(key,)).fetchone()
            if row and row[0] in ('running','failed') and completed_job(ROOT,key):
                db.execute("UPDATE jobs SET state='drafted',updated=? WHERE day=?",(dt.datetime.now(dt.timezone.utc).isoformat(),key));db.commit();row=('drafted',)
            due=day<now.date() or now.time().replace(tzinfo=None)>=draft_time
            if args.list:
                pr=db.execute('SELECT state FROM pr_jobs WHERE day=?',(key,)).fetchone();print(key,category,(row[0] if row else ('pending' if due else 'not due')),'PR:',pr[0] if pr else 'none');continue
            if row and row[0]=='drafted':submit_pr(db,ROOT,key,category,cfg,args.retry_pr_failed)
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
            if status=='drafted':submit_pr(db,ROOT,key,category,cfg,args.retry_pr_failed)
    return 0
if __name__=='__main__':raise SystemExit(main())

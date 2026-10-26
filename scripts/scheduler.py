#!/usr/bin/env python3
"""Persistent draft preparation scheduler. Never publishes or wakes the computer."""
import argparse
import datetime as dt
import sqlite3
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo('Asia/Kolkata')

def slot(day):
    if day.weekday() == 0: return 'ai'
    if day.weekday() == 2: return 'cyber'
    if day.weekday() == 4: return 'gaming' if day.isocalendar().week % 2 else 'dev'
    return None

def due_days(today, days=7):
    return [(d, slot(d)) for n in range(days, -1, -1) if slot(d := today - dt.timedelta(days=n))]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--lookback-days', type=int, default=7)
    p.add_argument('--list', action='store_true')
    p.add_argument('--retry-failed', action='store_true')
    args = p.parse_args()
    if not 0 <= args.lookback_days <= 30: p.error('lookback must be 0..30 days')
    (ROOT / 'data').mkdir(exist_ok=True)
    with sqlite3.connect(ROOT / 'data' / 'schedule.sqlite3', timeout=5) as db:
        db.execute('CREATE TABLE IF NOT EXISTS jobs (day TEXT PRIMARY KEY, category TEXT NOT NULL, state TEXT NOT NULL, updated TEXT NOT NULL)')
        for day, category in due_days(dt.datetime.now(ZONE).date(), args.lookback_days):
            key = day.isoformat()
            row = db.execute('SELECT state FROM jobs WHERE day=?', (key,)).fetchone()
            if args.list:
                print(key, category, row[0] if row else 'pending'); continue
            if row and not (args.retry_failed and row[0] == 'failed'): continue
            # Atomic claim prevents two scheduler processes running the same slot.
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            if row:
                changed = db.execute("UPDATE jobs SET state='running',updated=? WHERE day=? AND state='failed'", (now,key)).rowcount
            else:
                changed = db.execute("INSERT OR IGNORE INTO jobs VALUES (?,?,?,?)", (key,category,'running',now)).rowcount
            db.commit()
            if not changed: continue
            print('Preparing', key, category, flush=True)
            result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'blog.py'), '--category', category], cwd=ROOT)
            db.execute('UPDATE jobs SET state=?, updated=? WHERE day=?', ('drafted' if result.returncode == 0 else 'failed',dt.datetime.now(dt.timezone.utc).isoformat(),key)); db.commit()
    return 0

if __name__ == '__main__': raise SystemExit(main())

#!/usr/bin/env python3
"""Create a local non-overwriting backup of configuration, drafts and state."""
import argparse,datetime as dt,os,sqlite3,tempfile,zipfile
from contextlib import closing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def make_backup(root,destination):
 root=Path(root).resolve();destination=Path(destination).resolve();destination.parent.mkdir(parents=True,exist_ok=True)
 # Exclusive creation prevents accidentally replacing any prior backup.
 with destination.open('xb') as out:
  try:
   with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z, tempfile.TemporaryDirectory(prefix='ibrahimblog-backup-') as tmp:
    paths=[root/'config.json']
    for folder in ('drafts','data'):
     base=root/folder
     if base.exists():paths.extend(p for p in base.rglob('*') if p.is_file() and not p.is_symlink())
    for path in paths:
     if not path.is_file() or path.is_symlink() or path.resolve()==destination:continue
     rel=path.relative_to(root)
     if any((root/Path(*rel.parts[:i])).is_symlink() for i in range(1,len(rel.parts))):continue
     if path.name.endswith(('-wal','-shm','-journal')) or rel.parts[:2]==('data','logs'):continue
     if path.suffix=='.sqlite3':
      snapshot=Path(tmp)/(str(len(z.infolist()))+'.sqlite3')
      with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)) as source, closing(sqlite3.connect(snapshot)) as dest:source.backup(dest)
      z.write(snapshot,rel.as_posix())
     else:z.write(path,rel.as_posix())
  except BaseException:
   out.close();destination.unlink(missing_ok=True);raise
 return destination

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);args=p.parse_args()
 dest=args.output or ROOT/'backups'/('ibrahimblog-'+dt.datetime.now().strftime('%Y%m%d-%H%M%S')+'.zip')
 try:print('Backup created:',make_backup(ROOT,dest))
 except (OSError,sqlite3.Error) as exc:p.exit(1,'Backup failed: '+str(exc)+'\n')
if __name__=='__main__':main()

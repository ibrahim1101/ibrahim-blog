import sqlite3,sys,tempfile,unittest,zipfile
from contextlib import closing
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from backup import make_backup
class BackupTests(unittest.TestCase):
 def test_backup_contains_consistent_sqlite_and_refuses_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'root';root.mkdir();(root/'drafts').mkdir();(root/'data').mkdir();(root/'config.json').write_text('{}');(root/'drafts/story.md').write_text('draft')
   with closing(sqlite3.connect(root/'data/state.sqlite3')) as db, db:db.execute('create table sample (v text)');db.execute("insert into sample values ('kept')")
   out=Path(t)/'backup.zip';make_backup(root,out)
   with zipfile.ZipFile(out) as z:
    self.assertIn('drafts/story.md',z.namelist());self.assertIn('data/state.sqlite3',z.namelist());z.extract('data/state.sqlite3',Path(t)/'restore')
   with closing(sqlite3.connect(Path(t)/'restore/data/state.sqlite3')) as db:self.assertEqual(db.execute('select v from sample').fetchone()[0],'kept')
   with self.assertRaises(FileExistsError):make_backup(root,out)
if __name__=='__main__':unittest.main()

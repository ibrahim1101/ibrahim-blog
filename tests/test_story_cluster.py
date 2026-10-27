import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from story_cluster import canonical_url,similar
from candidates import connect,add
class Clusters(unittest.TestCase):
 def test_tracking_and_related_headlines(self):
  self.assertEqual(canonical_url('https://EXAMPLE.com/a/?utm_source=rss&id=5#top'),'https://example.com/a?id=5')
  self.assertTrue(similar('Vendor warns critical flaw affects 500 network routers','Critical vendor flaw affects 500 network routers'))
  self.assertFalse(similar('Vendor warns critical flaw affects 500 network routers','Critical vendor flaw affects 900 network routers'))
 def test_cluster_does_not_erase_sources(self):
  with tempfile.TemporaryDirectory() as t:
   db=connect(Path(t)/'q.db'); rows=[{'url':'https://a.example/x','title':'Vendor warns critical flaw affects 500 network routers','published':'2026-01-01'},{'url':'https://b.example/y','title':'Critical vendor flaw affects 500 network routers','published':'2026-01-01'}]
   self.assertEqual(add(db,'cyber',rows),2); clusters=[x[0] for x in db.execute('SELECT cluster_id FROM candidates')];self.assertEqual(clusters[0],clusters[1]);db.close()
if __name__=='__main__':unittest.main()

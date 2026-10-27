import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import blog
class RetrievalFailures(unittest.TestCase):
 def test_unavailable_source_is_recorded_without_breaking_research(self):
  original={'title':'Example story','url':'https://one.example/story','text':'Source text','outbound_links':['https://other.example/unavailable']}
  with patch.object(blog,'discover',return_value=[]),patch.object(blog,'get_page',side_effect=ValueError('failure')):
   docs=blog.gather_sources(original,[])
  self.assertEqual(len(docs),1);self.assertEqual(original['source_retrieval_failures'][0]['domain'],'other.example');self.assertEqual(original['source_retrieval_failures'][0]['error_type'],'ValueError')
if __name__=='__main__':unittest.main()

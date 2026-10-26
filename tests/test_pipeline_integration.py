import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import blog
class PipelineIntegration(unittest.TestCase):
 def test_official_host_policy_checks_domain_boundary(self):
  with patch.dict(blog.CONFIG, {'official_source_hosts':['cisa.gov']}):
   self.assertTrue(blog.is_official_candidate('https://www.cisa.gov/advisory'))
   self.assertTrue(blog.is_official_candidate('https://alerts.cisa.gov/advisory'))
   self.assertFalse(blog.is_official_candidate('https://cisa.gov.attacker.example/advisory'))
 def test_mocked_research_to_local_review_never_publishes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); one={'title':'Fixture vendor advisory','url':'https://vendor.example/story','published':'2026-01-01','feed':'fixture'}
   text='The vendor said that 50 devices may be affected. '+('The vendor reported a software problem in its product. '*8)
   other={'title':'Fixture independent report','url':'https://news.example/story','published':'2026-01-01','text':text}
   with patch.object(blog,'ROOT',root),patch.object(blog,'collect',return_value=[one]),patch.object(blog,'get_page',return_value=(text,one['url'],[])),patch.object(blog,'gather_sources',side_effect=lambda primary,candidates:[primary,other]),patch.object(blog,'ask',side_effect=['Vendor said 50 may be affected [SOURCE 1].','# Fixture vendor advisory\n\nThe vendor said 50 devices may be affected.\n\n## Sources\nhttps://vendor.example/story\nhttps://news.example/story','[]']),patch.object(sys,'argv',['blog.py','--category','cyber']):blog.main()
   reports=list((root/'drafts').glob('*.quality.json'));self.assertEqual(len(reports),1)
   report=json.loads(reports[0].read_text());self.assertFalse(report['publication_allowed']);self.assertEqual(report['status'],'REVIEW_REQUIRED');self.assertTrue(report['article_claim_review']);self.assertFalse((root/'website').exists())
if __name__=='__main__':unittest.main()

import json,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from approval_gate import touches_articles,has_owner_reviewer
SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'approval_gate.py'
class ApprovalGate(unittest.TestCase):
 def test_article_and_rename_detection(self):
  self.assertTrue(touches_articles([[{'filename':'elsewhere.md','previous_filename':'website/src/content/articles/old.md'}]]))
  self.assertFalse(touches_articles([[{'filename':'scripts/blog.py'}]]))
  self.assertTrue(touches_articles([[{'filename':'.github/workflows/editorial-gate.yml'}]]))
 def test_environment_requires_correct_owner_and_allows_self_review(self):
  environment={'name':'editorial','protection_rules':[{'type':'required_reviewers','prevent_self_review':False,'reviewers':[{'type':'User','reviewer':{'login':'ibrahim1101'}}]}]}
  self.assertTrue(has_owner_reviewer(environment,'ibrahim1101'));self.assertFalse(has_owner_reviewer(environment,'other'))
  environment['protection_rules'][0]['reviewers'].append({'type':'User','reviewer':{'login':'other'}});self.assertFalse(has_owner_reviewer(environment,'ibrahim1101'));environment['protection_rules'][0]['reviewers'].pop()
  environment['protection_rules'][0]['prevent_self_review']=True;self.assertFalse(has_owner_reviewer(environment,'ibrahim1101'))
  self.assertFalse(has_owner_reviewer({},'ibrahim1101'))
 def test_incomplete_file_listing_fails_closed(self):
  with tempfile.TemporaryDirectory() as t:
   p=__import__('pathlib').Path(t)/'files.json';p.write_text(json.dumps([[{'filename':'README.md'}]]))
   run=subprocess.run([sys.executable,str(SCRIPT),'files',str(p),'--changed-count','2'],capture_output=True)
   self.assertNotEqual(run.returncode,0)
if __name__=='__main__':unittest.main()

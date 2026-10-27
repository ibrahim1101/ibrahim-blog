import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from editorial import source_provenance,quality_report
from review import review_article
class EvidenceChecks(unittest.TestCase):
 def test_unknown_citation_and_long_copy_are_flagged(self):
  source='The organization announced that the incident affected numerous systems and that investigators were continuing their work to understand the scope and impact on users.'
  docs=[{'url':'https://example.com/original','text':source}]
  draft='# Headline\n\n'+source+'\n\n[Extra](https://unknown.example/story)\n\n## Sources\nhttps://example.com/original'
  flags=quality_report(draft,docs,source_provenance(docs),[])['flags']
  self.assertTrue(any('not in retrieved' in f for f in flags));self.assertTrue(any('copied' in f.lower() for f in flags))
 def test_negation_mismatch_is_advisory(self):
  x=review_article('The vendor said its production systems were compromised.',[{'text':'The vendor said its production systems were not compromised.'}]);self.assertTrue(any('negation' in f for f in x[0]['flags']));self.assertFalse(x[0]['human_verified'])
if __name__=='__main__':unittest.main()

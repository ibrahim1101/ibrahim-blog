import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'scripts'))
from editorial import source_provenance,quality_report,clean_extraction
first={'url':'https://www.bleepingcomputer.com/story','title':'Breach','text':'Information may have been exposed. There is no indication operational systems were affected.'}
second={'url':'https://mezha.net/story','title':'Breach','text':'This is reported by BleepingComputer. Hackers accessed a test environment.'}
p=source_provenance([first,second]); assert p[1]['explicitly_attributes_to']==['bleepingcomputer.com'],p
r=quality_report('# Head\n\nData were exposed.\n\n## Sources\nhttps://www.bleepingcomputer.com/story\nhttps://mezha.net/story',[first,second],p,[])
assert r['publication_allowed'] is False
assert any('dependency' in x.lower() for x in r['flags'])
assert any('certainty inflation' in x.lower() for x in r['flags'])
assert clean_extraction('Useful\nGet the report\nAdvertisement')=='Useful'
assert source_provenance([first,{'url':'https://example.org/x','text':'Independent text'}])[1]['provenance']=='unverified'
print('Editorial regression tests passed')
from review import review_article
from scheduler import slot, due_days
import datetime as dt
review = review_article('The university said information was exposed.', [{'text':'The university said information may have been exposed.'}])
assert review and any('certainty' in f for f in review[0]['flags']), review
assert review[0]['human_verified'] is False
assert review_article('The system affected 900 users.', [{'text':'The system affected 300 users.'}])[0]['status']=='UNVERIFIED'
assert slot(dt.date(2026,10,26)) == 'ai'
assert slot(dt.date(2026,10,28)) == 'cyber'
assert len(due_days(dt.date(2026,10,30), 7)) == 4
print('Claim review and scheduler regression tests passed')

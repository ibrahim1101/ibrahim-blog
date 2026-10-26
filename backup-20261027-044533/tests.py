import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from quality import clean_extraction, check_draft

sample = '''The University reported a breach.\nMore details about the incident.\nOnce attackers have valid credentials, only 37% of their actions are blocked\nOverall prevention scores can hide what happens after initial access.\nGet the report'''
assert clean_extraction(sample) == 'The University reported a breach.\nMore details about the incident.'
report = check_draft('# Story\n\n## Sources\nhttps://example.com/a', [{'url':'https://example.com/a'}], 'Story')
assert report['status'] == 'REVIEW_REQUIRED'
assert any('two distinct' in f for f in report['flags'])
print('Quality checks passed')

"""Advisory evidence checks; every result still requires human review."""
import re
from difflib import SequenceMatcher
from urllib.parse import urlsplit

SENTENCE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')
UNCERTAIN = re.compile(r'\b(may|might|could|possibly|possible|alleged|reportedly|no indication|not known|unconfirmed)\b', re.I)
NUMBERS = re.compile(r'\b(?:CVE-\d{4}-\d{4,}|\d+(?:[.,]\d+)*(?:%|\s*(?:million|billion))?)\b', re.I)

def sentences(text):
    text = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'(?m)^\s*(?:#+\s*|[-*]\s*)', '', text)
    return [s.strip() for s in SENTENCE.split(re.sub(r'\s+', ' ', text)) if len(s.strip()) > 25]

def tokens(text):
    return set(re.findall(r'[a-z0-9]{4,}', text.lower())) - {'that','this','with','from','their','about','have','were','which','will','would','been','they','said','according'}

def review_article(draft, documents):
    # Exact excerpts are presented to the human; similarity is not proof of support.
    before_sources = re.split(r'(?im)^##\s+(?:sources|references)\b', draft)[0]
    evidence = [(i, s) for i, d in enumerate(documents, 1) for s in sentences(d.get('text', ''))]
    ledger = []
    for claim in sentences(before_sources):
        if claim.startswith('<!--') or claim.startswith('#'): continue
        ct = tokens(claim)
        ranked = sorted(((len(ct & tokens(s)) / max(1, len(ct)), i, s) for i,s in evidence), reverse=True)
        match = ranked[0] if ranked and ranked[0][0] >= .35 else None
        flags = []
        if match:
            _, source_id, passage = match
            cn = {x.lower() for x in NUMBERS.findall(claim)}
            sn = {x.lower() for x in NUMBERS.findall(passage)}
            if cn - sn: flags.append('numbers or identifiers not present in matched passage')
            if UNCERTAIN.search(passage) and not UNCERTAIN.search(claim): flags.append('possible certainty inflation')
            status = 'PARTIALLY_SUPPORTED' if not flags else 'UNVERIFIED'
        else:
            source_id, passage, status = None, None, 'UNVERIFIED'
            flags.append('no candidate passage found')
        ledger.append({'claim': claim, 'status': status, 'candidate_source_id': source_id,
                       'exact_passage': passage, 'flags': flags, 'human_verified': False})
    return ledger

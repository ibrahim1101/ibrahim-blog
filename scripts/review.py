"""Evidence suggestions and conservative warnings, never a factual verdict."""
import re
SENTENCE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9])')
UNCERTAIN = re.compile(r'\b(may|might|could|possibly|possible|alleged|reportedly|no indication|not known|unconfirmed)\b', re.I)
NUMBERS = re.compile(r'(?i)\bCVE-\d{4}-\d{4,}\b|\b\d+(?:[.,]\d+)*(?:\s*(?:%|million|billion))?')
QUOTES = re.compile(r'[“"]([^”"\n]{12,})[”"]')
PROMO = re.compile(r'(?i)\b(sponsored content|advertisement|download (?:the|our) report|sign up for (?:our|the) newsletter)\b')

def sentences(text):
    text=re.sub(r'<!--.*?-->', ' ', text, flags=re.S)
    text=re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',text)
    # Headings are separate, reviewable claims, not discarded with first paragraph.
    blocks=[]
    for line in text.splitlines():
        line=re.sub(r'^\s*(?:#+\s*|[-*]\s*)','',line).strip()
        if line: blocks.extend(SENTENCE.split(line))
    return [s.strip() for s in blocks if len(s.strip())>20]

def tokens(text):
    return set(re.findall(r'[a-z0-9]{4,}', text.lower())) - {'that','this','with','from','their','about','have','were','which','will','would','been','they','said','according'}

def review_article(draft, documents):
    before_sources = re.split(r'(?im)^##\s+(?:sources|references|source links for editorial review)\b', draft)[0]
    evidence=[(i,s) for i,d in enumerate(documents,1) for s in sentences(d.get('text',''))]
    all_text='\n'.join(d.get('text','') for d in documents).lower()
    ledger=[]
    for claim in sentences(before_sources):
        ct=tokens(claim)
        ranked=sorted(((len(ct & tokens(s))/max(1,len(ct)),i,s) for i,s in evidence),reverse=True)
        match=ranked[0] if ranked and ranked[0][0]>=.35 else None
        flags=[]; source_id=None; passage=None
        if match:
            _,source_id,passage=match
            cn={x.lower().strip() for x in NUMBERS.findall(claim)}
            sn={x.lower().strip() for x in NUMBERS.findall(passage)}
            if cn-sn: flags.append('numbers or identifiers not present in matched passage')
            if UNCERTAIN.search(passage) and not UNCERTAIN.search(claim): flags.append('possible certainty inflation')
        else: flags.append('no candidate passage found')
        for quote in QUOTES.findall(claim):
            if quote.lower() not in all_text: flags.append('quotation not found verbatim in retrieved text')
        if PROMO.search(claim): flags.append('possible promotional content')
        # Lexical similarity only proposes a passage; it cannot establish support.
        ledger.append({'claim':claim,'status':'UNVERIFIED','candidate_source_id':source_id,'exact_passage':passage,'flags':flags,'human_verified':False})
    return ledger

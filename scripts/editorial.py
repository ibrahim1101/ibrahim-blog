"""Conservative editorial gates. This is NOT automated fact verification."""
import re
from urllib.parse import urlsplit

AD_PATTERNS = [r'^once attackers have valid credentials, only \d+%', r'^overall prevention scores can hide', r'^the blue report \d{4}', r'^get the report$', r'^advertisement$', r'^sponsored (?:content|by)', r'^other news you may find interesting:', r'^related articles:', r'^you may also like:']
ATTRIBUTION = [r'\b(?:reported|reports|according to|source|via|originally published|first reported|as reported|citing|cites|h/t|hat tip|based on)\s+(?:by\s+)?(?:the\s+)?(?:report(?:ing)?\s+(?:of|from|at)\s+)?', r'photo source\s*:', r'\b(?:bleepingcomputer|reuters|associated press|ap news|techcrunch|the verge|wired|arstechnica)\b']

def domain(url):
    host=(urlsplit(url).hostname or '').lower()
    return host[4:] if host.startswith('www.') else host

def clean_extraction(text):
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if any(re.search(p,line.strip(),re.I) for p in AD_PATTERNS):
            return '\n'.join(lines[:i]).strip()
    return text.strip()

def source_provenance(documents):
    """Find explicit credit and substantial shared passages. Neither establishes independence."""
    results=[]
    def chunks(body):
        # Long exact passages reduce false positives; still only a syndication signal.
        words=re.findall(r"[a-z0-9]+",body.lower())
        return {" ".join(words[i:i+18]) for i in range(0,max(0,len(words)-17),6)}
    for i,d in enumerate(documents):
        body=d.get('text',''); excerpt=body[:10000]; attributed=[]; attribution_evidence=[]; shared=[]
        for j,other in enumerate(documents):
            if i==j: continue
            other_domain=domain(other['url']); labels={other_domain,other_domain.split('.')[0],other.get('publisher','')}
            if other_domain=='bleepingcomputer.com': labels.add('BleepingComputer')
            for match in re.finditer(r'(?i)\b(?:reported by|according to|via|citing|source:|as reported by|originally published by|based on reporting from)\s*',excerpt):
                window=excerpt[match.end():match.end()+110]
                if any(x and x.lower() in window.lower() for x in labels):
                    attributed.append(other_domain); attribution_evidence.append(excerpt[max(0,match.start()-30):match.end()+110].strip())
            common=chunks(body)&chunks(other.get('text',''))
            if len(common)>=2: shared.append({'domain':other_domain,'shared_18_word_passages':len(common),'example':sorted(common)[0]})
        results.append({'url':d['url'],'domain':domain(d['url']),'explicitly_attributes_to':sorted(set(attributed)),'attribution_evidence':attribution_evidence[:5],'potential_syndication':shared,'provenance':'downstream' if attributed else 'unverified','note':'No detected attribution or overlap does not establish independence; shared material may be a common quotation.'})
    return results

def quality_report(draft, documents, provenance, claims):
    flags=[]
    domains=sorted({domain(d['url']) for d in documents})
    if len(domains)<2: flags.append('Only one distinct source domain.')
    downstream=[p for p in provenance if p['explicitly_attributes_to']]
    if downstream: flags.append('Source dependency: one publication explicitly attributes reporting to another collected publication.')
    if any(p.get('potential_syndication') for p in provenance): flags.append('Potential syndication or shared passages require manual inspection.')
    if not any(p['provenance']=='verified_primary' for p in provenance): flags.append('No independently verified official primary statement collected.')
    if len(documents)<2: flags.append('Only one retrievable source.')
    if not re.search(r'(?m)^#\s+\S',draft): flags.append('Missing H1.')
    if not re.search(r'(?im)^##\s+(?:sources|references)\b',draft): flags.append('Missing Sources heading.')
    for d in documents:
        if d['url'] not in draft: flags.append('Missing source URL: '+d['url'])
    if len(draft.split())<300: flags.append('Draft under 300 words; review completeness.')
    if re.search(r'(?i)blue report 2026|338 million simulations|37% of (?:an )?attacker',draft): flags.append('Advertisement contamination.')
    if re.search(r'(?i)\b(yesterday|last tuesday|last friday|last week)\b',draft): flags.append('Relative date left in draft.')
    combined=' '.join(d.get('text','') for d in documents).lower()
    if 'may have been exposed' in combined and re.search(r'(?i)\b(?:data|information|details|records)\s+(?:were|was|has been|had been)\s+exposed\b',draft): flags.append('Certainty inflation: source says information may have been exposed.')
    if 'no indication' in combined and re.search(r'(?i)(?:ensur(?:ed|ing)|confirm(?:ed|ing)|proved|verified)\s+that\s+(?:no|none of the)\s+(?:systems|operational)',draft): flags.append('Certainty inflation: source says no indication of operational compromise.')
    # Model-written claim table is advisory; all claims must be human checked.
    if not claims: flags.append('No structured claim ledger generated.')
    else:
        for c in claims:
            if not isinstance(c,dict) or not c.get('claim') or not c.get('source_ids') or c.get('status')!='needs_review' or not c.get('exact_passage_found'):
                flags.append('Claim ledger contains ungrounded or malformed claims.')
                break
    return {'status':'REVIEW_REQUIRED','publication_allowed':False,'automatic_publication_permitted':False,'source_count':len(documents),'distinct_source_domains':domains,'provenance':provenance,'claim_ledger':claims,'flags':flags,'editorial_verdict':'Human verification required. Source diversity is not independent corroboration.','manual_review_checklist':['Open and check the official primary announcement.','Confirm each factual claim against linked source passages.','Check source dependence and syndication.','Preserve may/could/reported and no indication qualifiers.','Verify dates, figures, and the nature of access codes.']}

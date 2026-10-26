"""Conservative source hygiene and draft QA. Flags issues; never certifies facts."""
import re
from urllib.parse import urlsplit

AD_PATTERNS = [
    r'(?im)^once attackers have valid credentials, only \d+%.*$',
    r'(?im)^overall prevention scores can hide.*$',
    r'(?im)^the blue report \d{4}.*$',
    r'(?im)^get the report\s*$',
    r'(?im)^sponsored (?:content|by).*$',
    r'(?im)^advertisement\s*$',
    r'(?im)^subscribe to (?:our|the) newsletter.*$',
]


def clean_extraction(text):
    """Strip known promotional blocks; don't claim to solve arbitrary ad extraction."""
    lines = text.splitlines()
    first_ad = next((i for i, line in enumerate(lines) if any(re.search(p, line) for p in AD_PATTERNS)), None)
    if first_ad is not None:
        lines = lines[:first_ad]
    return '\n'.join(lines).strip()


def domain(url):
    host = (urlsplit(url).hostname or '').lower()
    return host[4:] if host.startswith('www.') else host


def check_draft(draft, documents, primary_title):
    domains = sorted({domain(d['url']) for d in documents})
    source_urls = [d['url'] for d in documents]
    flags = []
    if len(domains) < 2:
        flags.append('Fewer than two distinct source domains; no independent corroboration.')
    if len(documents) < 2:
        flags.append('Only one retrieved source.')
    if not re.search(r'(?m)^#\s+\S', draft):
        flags.append('Missing Markdown H1 heading.')
    if not re.search(r'(?im)^##\s+(sources|references)\b', draft):
        flags.append('Missing Sources/References heading.')
    linked = [u for u in source_urls if u in draft]
    if len(linked) < len(source_urls):
        flags.append('Not all collected sources are linked in the article.')
    if re.search(r'(?i)blue report 2026|338 million simulations|37% of (?:an )?attacker', draft):
        flags.append('Potential advertisement contamination in generated article.')
    if len(draft.split()) < 350:
        flags.append('Short article; check whether enough verified detail exists.')
    if re.search(r'(?im)^\s*\[SOURCE \d+\]\s*TITLE:', draft):
        flags.append('Raw research packet leaked into article.')
    return {
        'status': 'REVIEW_REQUIRED',
        'source_count': len(documents),
        'distinct_source_domains': domains,
        'source_links_in_draft': len(linked),
        'flags': flags,
        'manual_review_checklist': [
            'Confirm important figures and dates against the linked originals.',
            'Find an official primary source if available; verify its exact claims.',
            'Check all quotations, CVEs, severity ratings and product names.',
            'Check that uncertainty (may/could/reported) is preserved.',
            'Check for ads, irrelevant material and copied wording.',
        ],
        'note': 'Automated checks are heuristic and do not prove factual accuracy.'
    }

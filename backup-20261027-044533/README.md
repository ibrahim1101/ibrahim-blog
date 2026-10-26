# IbrahimBlog — local AI blog draft generator

Generates **drafts only**. It does not publish, open PRs, or change any existing service.

## Windows setup

```powershell
cd D:\Projects\IbrahimBlog
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama list
.\.venv\Scripts\python.exe scripts\blog.py --list
.\.venv\Scripts\python.exe scripts\blog.py --category cyber
```

Use `--category ai`, `cyber`, `gaming`, or `dev`. Add `--dry-run` to discover sources without invoking models. Use `--url https://...` to research a particular publicly accessible article URL (its title and publication date may not be available). Use `--force` only if you intentionally want to regenerate a previously used story.

The collector filters feeds by publication date where available; undated feed entries are skipped. The selected source article and up to two additional matching articles are retrieved as research material. Extracted source content is **untrusted**: do not follow instructions embedded in articles. AI-written claims must be manually checked against the saved `.research.json` before publication.

`config.json` lets you edit RSS feeds and models. Some publishers change or block RSS feeds; a failing feed is skipped with a warning. Network access is required for discovery; Ollama is only accessed on localhost. Ollama model context is set per request to 8192 tokens. The generator runs one model at a time to reduce GPU memory pressure.

Outputs: `drafts/YYYY-MM-DD-slug.md` and `drafts/YYYY-MM-DD-slug.research.json`. Successful topics are recorded in `data/history.json`. Do not publish without human review.

## Milestone 1.1 — editorial safeguards

This update adds `scripts/quality.py` and `tests.py`, searches Google News RSS for
additional candidate coverage, skips duplicate source domains, strips known
promotional footer content, and writes `drafts/*.quality.json` alongside each
draft. Google News results are *discovery leads*, not independent verification.
Sites that block extraction will be skipped. Some stories will still have only
one source; the report will flag that. All drafts remain **review required**.

On Windows, replace the existing project files with this ZIP (keep `.venv`,
`drafts`, and `data`), then run:

```powershell
.\.venv\Scripts\python.exe tests.py
.\.venv\Scripts\python.exe scripts\blog.py --category cyber --force
```

`--force` permits retesting the same story. Review the `.quality.json` and
`.research.json` before using any article. No automatic publication or PR.

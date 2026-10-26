# IbrahimBlog

A local-first technology-news workflow and static Astro publication. Research and generated drafts remain private local files. Every draft requires human editorial review; the tools do not publish, merge, or approve an article automatically.

## Start on Windows

Install Python 3.11+ and Node.js 22+, and have Ollama running locally with `qwen3:8b` and `qwen3:14b`. From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\validate.ps1
.\.venv\Scripts\python.exe scripts\blog.py --category cyber --list
```

To preview the website locally:

```powershell
cd website
npm run dev
```

Read [Operations](docs/OPERATIONS.md), [Editorial](docs/EDITORIAL.md), [Deployment](docs/DEPLOYMENT.md), and [Status and limitations](DEVELOPMENT_STATUS.md) before enabling scheduled work or deploying. No public posts are included by default. Preserve any existing drafts before copying this project over another installation; do not overwrite your current project blindly.

## Components

- `scripts/blog.py`: collects feeds and source excerpts, calls loopback Ollama, produces local Markdown, evidence and quality reports.
- `scripts/safe_fetch.py`: bounds public source retrieval, resolves and pins public network addresses, validates redirects, uses TLS verification.
- `scripts/review.py`, `scripts/editorial.py`: conservative advisory checks; these do not establish factual truth or grant publication approval.
- `scripts/scheduler.py`: persistent scheduled draft slots, no publishing.
- `scripts/editor.py`: local review and manual staging of articles into a review branch.
- `website/`: static Astro publication, empty until content is deliberately staged and merged.
- `.github/workflows/checks.yml`: validation only; no auto-approval or deployment.

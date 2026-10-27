# Operations

## Local models and sources

`config.json` holds feed URLs, freshness limits, Ollama models and context size. The current default assignments are qwen3:8b for research and qwen3:14b for writing. Pull them using `ollama pull qwen3:8b` and `ollama pull qwen3:14b`. The client requires a loopback Ollama HTTP address; do not expose the server publicly. Inference performance depends on the local GPU and model configuration.

```powershell
.\.venv\Scripts\python.exe scripts\blog.py --category ai --list
.\.venv\Scripts\python.exe scripts\blog.py --category cyber --dry-run
.\.venv\Scripts\python.exe scripts\blog.py --category cyber
.\.venv\Scripts\python.exe scripts\editor.py list
```

`--dry-run` retrieves sources but does not call Ollama or generate a draft. `--force` allows a previously seen URL and creates a different output filename. Do not use it for routine generation. Each successful generation produces Markdown plus research and quality JSON in `drafts/`. The reports are advisory and all source text is untrusted. The source fetcher validates every address and redirect, pins the connected IP, and bounds responses; this reduces risk but should not be treated as a security guarantee. Source relevance, independent corroboration and primary-source discovery remain imperfect; a single configured official-source host can produce a draft, but its official role and every assertion still require human verification. Two domains are not automatically independent. Fetch errors or insufficient sources cause a skipped draft.

## Schedule

```powershell
.\.venv\Scripts\python.exe scripts\scheduler.py --list
.\.venv\Scripts\python.exe scripts\scheduler.py
.\.venv\Scripts\python.exe scripts\scheduler.py --retry-failed
```

The `schedule` section of `config.json` sets the time zone, draft time, lookback and optional failed-job retries. A task invocation processes up to seven days of due Monday AI, Wednesday cyber, and alternating Friday gaming/dev slots in Asia/Kolkata. Friday parity follows ISO week numbers. Install the optional Windows task with `powershell -ExecutionPolicy Bypass -File .\scripts\install-schedule.ps1`. It triggers daily at 10:15 local time and at logon, uses your logged-in user, ignores overlapping invocations and does not wake or shut down the PC. Logs are written under `data/logs/`. The script refuses to overwrite an existing task. Change `-DailyTime` or the config draft time if needed. Confirm Ollama is running under the selected user. Job claims are recorded in `data/schedule.sqlite3` to prevent concurrent duplicate execution. Completed jobs write a manifest with hashes of the three outputs; on the next scheduler invocation a valid manifest lets it reconcile an interrupted or failed job to drafted without regenerating. If there is no valid manifest, the slot remains `running`: inspect drafts and logs before any manual retry. Failure retries are explicit, not automatic. Each job has a two-hour limit. A hard interruption may leave a slot in `running`, deliberately requiring inspection before retry; the system does not currently provide a candidate queue.

## Backup and maintenance

Create a local backup with `.\.venv\Scripts\python.exe scripts\backup.py`. It saves configuration, drafts and state into a new ZIP under `backups/`, uses SQLite’s backup API, excludes logs, and never overwrites an existing ZIP. Stop the scheduler while backing up so related files represent the same point in time. Store the archive privately, as it contains drafts and research. To restore, extract into a separate empty directory, compare its contents, then copy the desired files into a stopped installation without overwriting newer work. Never commit draft evidence, private credentials, databases, or the virtual environment. Python installs use the pinned `requirements-lock.txt`, and the website uses its npm lockfile. Update both deliberately, rerun validation, and monitor vulnerabilities; version pinning does not itself establish security.

## Candidate queue

Collect multiple headlines without generating or publishing articles, then select one:

```powershell
.\.venv\Scripts\python.exe scripts\candidates.py collect --category cyber
.\.venv\Scripts\python.exe scripts\candidates.py list
.\.venv\Scripts\python.exe scripts\candidates.py generate <candidate-id>
.\.venv\Scripts\python.exe scripts\candidates.py reject <candidate-id>
```

The queue is local SQLite and removes common tracking parameters before exact-URL deduplication. It groups conservatively similar headlines for review without treating different domains as independent sources. Generation claims a candidate before starting; a crash can leave it `GENERATING`, so inspect outputs before manually repairing its state. A selected candidate may still fail retrieval or editorial checks. It creates a review-required local draft, never a public article.

## Scheduled draft pull requests

The `schedule.automatic_draft_pr` setting enables draft PR creation after a complete scheduled draft. The PR command uses an isolated worktree and sends the article only; research JSON remains local. Git and authenticated `gh` must be installed on the PC. Because your repository is public, `schedule.allow_public_draft_pr` defaults to `false`: the PR attempt fails closed rather than expose a draft. Set it to `true` only if you want anyone to see drafts in public PRs and previews. A PR is never merged automatically.

Each job gets one recorded PR attempt. To see states, run `scripts\scheduler.py --list`. If an attempt fails, inspect its branch, worktree and GitHub PRs before using `--retry-pr-failed`; a process killed during a PR attempt remains `running` and requires investigation to prevent duplicates. The scheduled placeholder publication date and all article content must be edited during human review.

Article fetches consult `robots.txt` and apply process-local per-host pacing. A missing robots file is treated as allowing access; a denied or unavailable policy fails closed, including on redirects. Feed availability and site policies can change; configure sources responsibly. The policy is not a substitute for complying with each site’s terms.

## Article formats and roundups

Use `scripts\blog.py --category cyber --format advisory` to request a specific format. Supported formats are `news`, `breaking`, `advisory`, `explainer`, `product`, `release`, `hardware`, `gaming`, and `analysis`. The system adjusts the writing instruction; the format does not certify the facts.

For a weekly roundup, select two to four existing draft filenames with their evidence files:

```powershell
.\.venv\Scripts\python.exe scripts\roundup.py '<draft-1>.md' '<draft-2>.md' --category ai
```

The roundup is a new review-required draft and uses the selected stories’ local source evidence. It never automatically publishes or independently verifies the sources.

## Dependency audits and URL records

To audit the pinned Python dependencies, install the `pip-audit` tool separately and run `python -m pip_audit -r requirements-lock.txt`. For the site, run `npm --prefix website audit --omit=dev`. Audits are point-in-time checks; review update PRs and rerun validation before deployment.

Each retrieved source records its retrieval timestamp, final fetched URL and a normalized URL with common tracking parameters removed. The normalized URL is marked `normalized_not_verified`: it is not an independently verified publisher-declared canonical URL. Failed secondary-source fetches are recorded by domain and error type, without treating missing sources as corroboration.

## Source preferences

The `source_policies` entries in `config.json` support `enabled`, `role` (`official_candidate`, `secondary`, or `unverified`) and a 0–100 priority. The most specific matching domain wins. Disabled sources are blocked before article requests, including redirects. Freshness takes precedence over source priority; the priority is an editorial preference within the same date, not a factual reliability score. An official-domain match only identifies a possible primary source and must be verified by the editor. Unknown domains remain unverified.

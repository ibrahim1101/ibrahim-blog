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

The `schedule` section of `config.json` sets the time zone, draft time, lookback and optional failed-job retries. A task invocation processes up to seven days of due Monday AI, Wednesday cyber, and alternating Friday gaming/dev slots in Asia/Kolkata. Friday parity follows ISO week numbers. Set a Windows Task Scheduler trigger at your preferred local time, using program `D:\Projects\IbrahimBlog\.venv\Scripts\python.exe`, argument `D:\Projects\IbrahimBlog\scripts\scheduler.py`, and working directory `D:\Projects\IbrahimBlog`. Also trigger at logon to catch up. Disable wake-to-run; it never wakes or shuts down your PC. Confirm Ollama is running under the selected user. Job claims are recorded in `data/schedule.sqlite3` to prevent concurrent duplicate execution. Completed jobs write a manifest with hashes of the three outputs; on the next scheduler invocation a valid manifest lets it reconcile an interrupted or failed job to drafted without regenerating. If there is no valid manifest, the slot remains `running`: inspect drafts and logs before any manual retry. Failure retries are explicit, not automatic. Each job has a two-hour limit. A hard interruption may leave a slot in `running`, deliberately requiring inspection before retry; the system does not currently provide a candidate queue.

## Backup and maintenance

Back up `config.json`, `drafts/`, and `data/` regularly while the scheduler is stopped. SQLite backups should use SQLite's backup API or a cleanly stopped process. Restore those files into a fresh installation. Never commit draft evidence, private credentials, databases, or the virtual environment. Update dependencies deliberately and run validation after updates. The included Python and npm dependency constraints are not a substitute for vulnerability monitoring.

## Candidate queue

Collect multiple headlines without generating or publishing articles, then select one:

```powershell
.\.venv\Scripts\python.exe scripts\candidates.py collect --category cyber
.\.venv\Scripts\python.exe scripts\candidates.py list
.\.venv\Scripts\python.exe scripts\candidates.py generate <candidate-id>
.\.venv\Scripts\python.exe scripts\candidates.py reject <candidate-id>
```

The queue is local SQLite and deduplicates exact URLs. Generation claims a candidate before starting; a crash can leave it `GENERATING`, so inspect outputs before manually repairing its state. A selected candidate may still fail retrieval or editorial checks. It creates a review-required local draft, never a public article.

# Editorial workflow

1. Run `python scripts/editor.py list` and then `python scripts/editor.py show <draft-filename>`. Open the original evidence links; read the complete quality report, source passages, and article. Confirm every claim, number, quote, date, uncertainty and source relationship. An automated ledger is not proof. Reject or rewrite unsupported content; perform additional research independently when needed. Do not include private evidence in a public repository.
2. Start from a clean production branch, create a review branch, and stage a reviewed draft:

```powershell
git switch main
git switch -c review/my-story
.\.venv\Scripts\python.exe scripts\editor.py stage '<draft filename>.md' --title 'Reviewed title' --description 'Accurate summary' --category cyber --date '2026-10-27'
```

The command asks you to type `STAGE`. Staging copies the article to the website content folder; it is **not** human approval. Edit the staged Markdown and metadata, including disclosure and sources, to reflect your actual review. Check the local build with `.\validate.ps1`.
3. Commit only the intended website article, push the review branch, then run `gh pr create --draft --title "Review: story title" --body "Editorial review required. Check every claim and source before publication."`. Open the PR, verify the actual changes, and finish human review. Do not commit the private `drafts/`, evidence or local database.
4. Only after your explicit editorial decision, mark the PR ready, obtain whatever review the repository rules require, and manually merge it. Configure branch protection/rulesets to prevent direct pushes and require review, status checks and no bypass where the account permits. A self-review cannot satisfy GitHub's normal required-review rule for your own PR; use an eligible second reviewer or choose a different authenticated approval mechanism. CI success, a label or a model-generated report is not approval.

The build renders all Markdown files under `website/src/content/articles`; it cannot by itself distinguish a reviewed file from an unreviewed one. **The required security boundary is repository permissions, protected production branch, and Cloudflare production deployment restricted to that branch.** Until those account settings are verified, unapproved content could be published by a direct push or unsafe deployment configuration. PR previews may expose staged content; disable public previews or use access control if needed.

For corrections, edit an existing article on a review branch, add an `updated` date and a clearly visible correction note, and repeat review and merge. No automatic publication feature exists in this project.

## Local review history

After checking the draft and its evidence, record an advisory local decision:

```powershell
.\.venv\Scripts\python.exe scripts\editor.py decision '<draft filename>.md' --state REVIEWED --reviewer 'Shaik Ibrahim' --note 'Checked each claim and original source'
.\.venv\Scripts\python.exe scripts\editor.py history '<draft filename>.md'
```

REVIEWED, NEEDS_REVISION and REJECTED are local audit notes, not authenticated approval or a publish command. The status returns to REVIEW_REQUIRED when the draft, research evidence or quality report changes. The append-only event list is local SQLite and is not tamper-proof. GitHub permissions and branch protection are still required for publication.

## Create a draft pull request

After reviewing or selecting a local draft, install and authenticate the GitHub CLI (`gh`) with the minimum necessary repository permissions. Use a checkout whose `origin` points to the intended repository. This command fetches `main`, creates a separate temporary worktree and branch, stages only the article, commits, pushes, and opens a **draft** PR; it never approves or merges:

```powershell
.\.venv\Scripts\python.exe scripts\create_review_pr.py '<draft filename>.md' --title 'Story title' --description 'Accurate summary' --category cyber --date '2026-10-27' --repo ibrahim1101/ibrahim-blog
```

Public repositories expose PR contents and possibly preview deployments. The command refuses public repositories unless the operator explicitly adds `--allow-public`. Evidence JSON remains local. The scheduler can invoke this command automatically when configured; its public-repository guard remains in force. If any step fails, inspect the branch and working tree before retrying. A public PR or a CI pass does not represent editorial approval.

Website builds reject raw HTML and obvious unsafe link schemes in article Markdown, and source metadata is restricted to HTTP(S). These checks reduce risk but do not replace editorial review or a security audit.

## Request further work

```powershell
.\.venv\Scripts\python.exe scripts\editor.py research '<draft filename>.md'
.\.venv\Scripts\python.exe scripts\editor.py regenerate '<draft filename>.md'
```

`research` retrieves a fresh, separate evidence packet using the original source. Review that packet independently; it does not change the draft or automatically certify claims. `regenerate` runs the pipeline again for the original topic and creates new draft and report files rather than replacing the original. Both require network access; regeneration also requires local Ollama.

# Development status and release limitations

Implemented locally: existing Python/Ollama pipeline retained; public-address-pinned and bounded source fetches; advisory source and article claim review; a persistent draft-only scheduler; CLI review/staging workflow; Astro publication with categories, search, RSS, sitemap, policy pages, article sources, metadata, structured data and responsive styling; optional Cloudflare Pages contact function; and CI validation configuration. Preserved existing drafts and backups. No article has been published.

Offline tests cover representative source dependency and uncertainty cases, IP and redirect rejection, staging and advisory gate behavior, contact verification with mocks, and a fictional article build. These do not establish comprehensive fact-checking or security. Real feed collection, Ollama inference, Windows Task Scheduler, GitHub PR and protection rules, Cloudflare deployment, live contact delivery, browser accessibility and responsive rendering were not validated in this environment.

Important remaining engineering: improve semantic claim verification and all-claim coverage; independently corroborate rather than rely on domain count; verify primary-source roles; add safe interrupted-job recovery and stronger clustering and near-duplicate detection; implement Cloudflare account provisioning and rate limiting; verify authenticated human approval rules in the actual repository; expand adversarial and end-to-end tests. The system has not been independently security audited. Automated checks are advisory, not fact checking. A verified protected production branch is needed to prevent bypass of human review.

The GitHub repository now exists. The original upload included drafts, evidence and backups in this public repository. Ignore rules only prevent future untracked files; they do not remove already tracked files or erase public history. Review repository visibility and previous commits before using real drafts. The website and its contact delivery remain unconfigured for live hosting. Keep drafts private and do not assume all requested features or live deployment are complete.

The website was upgraded to Astro 7 and Node 24 after a dependency audit. An npm production audit reported no known vulnerabilities at the time of the check; continue monitoring advisories.

Additional implementation: a local evidence-bound editorial audit trail, attribution/overlap warnings, output manifests for safe recovery of completed jobs, and a Cloudflare Email Service delivery worker with mocked tests. A local REVIEWED status is not authenticated publication approval. Actual email delivery and Cloudflare provisioning remain unverified.

The local candidate queue supports collection, selection, rejection and draft generation with exact-URL deduplication; it does not establish topic independence or near-duplicate similarity.

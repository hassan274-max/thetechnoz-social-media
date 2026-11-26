# TheTechnoz Solutions — direct personal LinkedIn publishing

## Scope
The user explicitly chose **personal LinkedIn only**, deferring company Page publishing.

- Two posts per day: advanced AI/LLM at 10:00 AM PKT and Amazon Private Label/PPC at 6:00 PM PKT.
- First 30-day trial. Unique LinkedIn-specific substantive content, not repeated Facebook captions.
- Direct first-party LinkedIn API via GitHub Actions; **no Metricool in publishing path**.
- Previously scheduled Metricool posts were changed into non-auto-publishing drafts.
- Workflow: `.github/workflows/linkedin-direct-daily.yml`.
- Publisher: `scripts/linkedin_direct_publish.py`.
- Queue: `linkedin-direct-queue.json` (currently four future original posts).
- Ledger: `linkedin-direct-log.json`, separately records attempted and confirmed publications.

## Activation — not yet authorized
The LinkedIn developer app has **Share on LinkedIn** enabled; it requires a separate OAuth user authorization to actually issue a personal-profile posting token with `w_member_social`.

Secrets must be configured in the repository's GitHub Actions Secrets, never committed to source:
- `LINKEDIN_ACCESS_TOKEN` — the user's authorized OAuth token with `w_member_social`.
- `LINKEDIN_PERSON_URN` — the actual authenticated member's `urn:li:person:<id>`.

A repository Actions variable `LINKEDIN_DIRECT_ENABLED=true` activates the uploader **only after** the token and member identifier have been verified. Until then, the workflow schedules dry/no-upload runs.

The application does **not** need `w_organization_social`, Community Management API, or a company Page token for this personal-only phase.

## No repetition and failure handling
Once an item has a ledger entry for the personal destination, it will not be sent again automatically. A persistent `attempted` claim is written and committed before each API request; if a result is uncertain, manual feed reconciliation is required before any retry. Posts not approved or missing from the queue are skipped.

## Official LinkedIn guidance
https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin

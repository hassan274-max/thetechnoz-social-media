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

## One-time local authorization (recommended)

The LinkedIn app has **Share on LinkedIn** enabled. For reliable confirmation of the authenticated member ID, also enable **Sign In with LinkedIn using OpenID Connect**; this is for member identity only, **not** the company-page Community Management API.

1. In LinkedIn Developer App → **Auth**, add this exact authorized redirect URL:
   `http://localhost:8765/linkedin-callback`
2. On the same app, ensure that `w_member_social`, `openid` and `profile` are shown among the available OAuth scopes.
3. On **your own computer**, install Python 3 and GitHub CLI (https://cli.github.com/), then sign in with `gh auth login`.
4. Clone the repository if not already cloned:
   `git clone https://github.com/hassan274-max/thetechnoz-social-media.git`
5. From the cloned folder run:
   `python scripts/linkedin_oauth_local.py`
6. Enter the Client ID and Client Secret in your **local terminal only**, consent to your LinkedIn account in the browser, then let the script save the OAuth access token and identified person URN as encrypted GitHub Actions secrets. It does **not** commit or print the credentials.
7. Before enabling publishing, verify the safe workflow at
   https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/linkedin-direct-daily.yml.
   It verifies the token and LinkedIn member identity on push/manual runs **without posting**.
8. Once both the identity check and publishing authorization are confirmed, set repository Actions variable `LINKEDIN_DIRECT_ENABLED` to `true` under Settings → Secrets and variables → Actions → Variables. **Don't do this yet** until the connection test is successful.

Only 4 unique original posts have been drafted so far. The remaining 26 days must be prepared without repetition. OAuth tokens may expire and require reauthorization. The local setup script only configures authorization, **it never publishes a LinkedIn post**.

References:
- https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow
- https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin

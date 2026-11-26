# TheTechnoz Solutions — direct LinkedIn personal + company posting

## Status (27 November 2026)
- **Direct pipeline created but not activated**; no LinkedIn access token is saved in the GitHub repository.
- Metricool's previously scheduled LinkedIn items were switched to drafts with autoPublish=false; Metricool is no longer part of the proposed delivery path.
- Four distinct original example posts are staged for 28–29 November at **10:00 AM AI/LLM** and **6:00 PM Amazon PPC** (Pakistan time), designed to publish **once to the personal profile and once to the company page** at each slot.
- Future 30-day content must be created and approved without reuse; do not assume 60 posts are already queued.
- GitHub workflow: `.github/workflows/linkedin-direct-daily.yml`.
- Direct official Posts API client: `scripts/linkedin_direct_publish.py`.
- Persistent per-post, per-author tracking: `linkedin-direct-log.json`.

## Permissions are different
1. **Share on LinkedIn** provides `w_member_social` for the authenticated personal member.
2. Company Page posting requires **`w_organization_social`**, ordinarily via the **Community Management API** product, which may require LinkedIn's access request and review. The authenticated person must have the applicable admin role on the Page.
3. Creating a developer application attached to a LinkedIn Page does *not* alone grant organization publishing access.
4. OAuth consent for these approved scopes must be completed. Existing Metricool authorization cannot be reused as this developer application's token.

## Secrets and activation
After authorizing the app, add these **GitHub Actions secrets** under Settings → Secrets and variables → Actions:
- `LINKEDIN_ACCESS_TOKEN`: OAuth access token for this application, with all approved posting scopes.
- `LINKEDIN_PERSON_URN`: authenticated member's actual `urn:li:person:<id>`.
- `LINKEDIN_ORGANIZATION_URN`: target company page's actual `urn:li:organization:<numeric-id>`.

The GitHub Actions **repository variable** `LINKEDIN_DIRECT_ENABLED` must be set to `true` only after confirming valid scope, user approval and IDs. The default missing/false state prevents API posting.

Do not paste access tokens or client secrets in ChatGPT or GitHub files. Tokens expire and may require fresh OAuth authorization. The access token and member ID must correspond to the same authenticated LinkedIn user.

The 2 daily cron schedules are registered but perform **no external uploads until LINKEDIN_DIRECT_ENABLED=true**. The manual dispatch is **dry run only**.

## Fail-safe and no-repeat policy
Each approved content ID is claimed in the Git ledger **before** its API call for each destination. A claim remains and blocks automatic retries when the result is uncertain. Publishing the same approved post once to personal and once to the company is expected cross-posting, not a repeat. A 403/401 on a destination is a stop condition, not grounds to retry automatically.

## Authoritative docs
- LinkedIn Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- Community Management access: https://learn.microsoft.com/en-us/linkedin/marketing/community-management-app-review
- Share on LinkedIn: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin

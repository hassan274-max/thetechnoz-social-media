# Direct LinkedIn publishing — migration checklist

User requested **no Metricool**. Publishing to their personal profile must happen through LinkedIn's own OAuth 2.0 and official API, not a third-party scheduler.

## Current status
- Not authorized; direct auto-publishing is **disabled**.
- The old Metricool calendar contains scheduled posts that must be removed or changed to drafts before enabling this direct workflow to prevent double-posting.
- No direct LinkedIn post has been uploaded and no direct daily schedule has been turned on.

## One-time authorization
1. In https://www.linkedin.com/developers/apps create a LinkedIn developer app linked to an eligible LinkedIn page.
2. Add the **Share on LinkedIn** product and ensure the application has `w_member_social`.
3. Authorize this personal LinkedIn account through LinkedIn OAuth. Do not paste tokens into public GitHub files or chats.
4. Store the token securely as GitHub Actions secret `LINKEDIN_ACCESS_TOKEN`, and the confirmed authenticated member's URN as `LINKEDIN_PERSON_URN`. Set `LINKEDIN_DIRECT_ENABLED=true` only after authorization and a private connectivity test.
5. Use one unique AI/LLM and one unique Amazon PPC post daily for 30 days with a permanent publishing ledger; never recycle captions or posts.
6. Access tokens expire; reauthorization may be needed. If token is invalid, fail safely and notify.

LinkedIn official guidance: https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin

**Never enable scheduled publication while Metricool posts remain pending**, since these could duplicate direct publication.

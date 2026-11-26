# TheTechnoz Solutions — approved daily YouTube publishing

**Status:** Active schedule for the 14-user-approved animated educational Shorts.

- Workflow: `.github/workflows/youtube-approved-daily.yml`
- Schedule: 13:00 UTC / **18:00 PKT**, daily (GitHub cron scheduling may occasionally start late).
- Approved publishing window: **2026-11-27 through 2026-12-10** (14 individual episodes), after which the workflow deliberately skips rather than repeats episodes.
- Topics alternate AI/LLM and Amazon Private Label/PPC.
- User-approved video style: question-led hook, meaningful animated lesson, closing Q&A, original music, Kokoro neural narration, consistent vertical design.
- Every run validates correct channel **UCIwmarXnoB7vvssN9OxEeDA**, then media, and creates a persistent claim in `youtube-publishing-log.json` **before** uploading. Confirmed video URLs are written back to the same file.
- If a video upload fails or its status is uncertain, the episode remains marked `attempted` and is **not** retried automatically. Inspect YouTube Studio manually to avoid duplicates.
- Pushing code or manually selecting **Run workflow** only tests the OAuth/channel connection; it does not upload. The cron schedule is the sole publishing path.
- Verified no-upload authorization preflight: GitHub Actions run **45887037964**, successful.
- The previously rejected slide-based tutorial workflow remains disabled. This approved schedule publishes **Shorts only**.
- YouTube OAuth access may expire or require renewed authorization, especially if the Google OAuth application is still in **Testing**. GitHub Actions will fail safely rather than publish via an unexpected account.
- A new editorial set or video duration/type requires separately developed content and a new review before the 14-video horizon is extended.

## Verification links

- Publishing workflow: https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/youtube-approved-daily.yml
- Source schedule: https://github.com/hassan274-max/thetechnoz-social-media/blob/main/scripts/youtube_editorial.py
- Posting ledger: https://github.com/hassan274-max/thetechnoz-social-media/blob/main/youtube-publishing-log.json

**As of setup, no scheduled public upload is claimed to have occurred yet.** The first due attempt is 27 November 2026 at approximately 18:00 Pakistan time, subject to GitHub's schedule execution and Google authorization.

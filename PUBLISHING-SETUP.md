# TheTechnoz Social Publisher (Meta)

This repository contains a scheduled, owner-controlled photo publisher for the Facebook Page **TheTechnoz Solutions** and its linked Instagram account. YouTube is not connected yet.

## Safety / setup
1. GitHub repo → **Settings → Secrets and variables → Actions → Secrets**: add `META_PAGE_ACCESS_TOKEN` with a **new, valid Facebook Page access token** for TheTechnoz Solutions. Never commit or share the token.
2. In the **Variables** tab add `PUBLISHING_ENABLED` = `false` initially.
3. Keep the Instagram-linked Facebook Page accessible to your app; ensure `pages_manage_posts`, `instagram_basic`, `instagram_content_publish` are granted.
4. Add **approved**, publicly hosted images and captions to `posts-queue.json`. An item example:
   ```json
   {"id":"launch-002","scheduled_at":"2026-12-01T06:00:00Z","image_url":"https://YOUR-USERNAME.github.io/thetechnoz-social-media/launch-002.png","path":"launch-002.png","caption":"Your approved caption","platforms":["facebook","instagram"]}
   ```
5. Go to **Actions → Publish scheduled Facebook and Instagram posts → Run workflow** with **dry_run=true**. Review the output.
6. Only after approval and token setup, change repository variable `PUBLISHING_ENABLED` to `true`; scheduled workflow checks at 11 AM and 7 PM Pakistan time.
7. Review Actions results and `publishing-log.json`; scheduled jobs can run late or fail. Add monitoring before relying on unattended business posting.

## How cleanup works
Assets listed in `assets-manifest.json` as successfully published with a delete_after of >=72 hours after published_at are eligible for cleanup. Social posts remain published on Meta. **Git history still retains old image blobs**, so this does not fully control repository storage. Use a bucket/CDN with true lifecycle deletion if storage grows.

## Limitations
- Posts are **not generated** automatically; only pre-approved queued posts are published.
- Current support: single image Facebook / Instagram posts. Reels, carousels and YouTube are not implemented.
- No posts are queued by default.
- If a request succeeds remotely but the process stops before committing its result, retries could duplicate a post; check the Facebook/Instagram feed before rerunning after an interrupted run.
- Meta tokens expire or can be invalidated. Reauthorization and token rotation must be maintained.
- Use scheduled times as a target, not a guarantee; GitHub may delay scheduled jobs.

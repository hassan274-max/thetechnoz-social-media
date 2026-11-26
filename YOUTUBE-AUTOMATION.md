# TheTechnoz Solutions — Automated YouTube publishing

## Current activation

- Scheduled GitHub workflow: `.github/workflows/youtube-scheduled.yml` (enabled on main).
- Channel checked before every upload: **TheTechnoz Solutions**, `UCIwmarXnoB7vvssN9OxEeDA`.
- **Daily Short at ~18:00 Pakistan time** (13:00 UTC), starting **27 Nov 2026**.
- **Saturday tutorial at ~15:00 Pakistan time** (10:00 UTC), starting **28 Nov 2026**.
- All uploads request `public` and are explicitly authorized through the workflow; initial manual tests remain private by default.
- First two weeks are supplied with **14 distinct Shorts and 2 tutorials** in `scripts/youtube_editorial.py`. **When the catalog is exhausted the workflow safely skips** rather than recycling the same content. Add reviewed original material for later dates.
- Content uses original scripted educational advice, Pillow-rendered slides, offline synthesized English voice narration using eSpeak NG, and FFmpeg. No licensed third-party videos or recorded music.
- The Short output is 720×1280; tutorials are 1280×720 and checked against a ~5–8-minute runtime target. If a render falls outside bounds, publication fails rather than upload a misleadingly short clip.
- Each video is generated on the GitHub runner at publication time, not committed to GitHub. That means GitHub source cleanup is not necessary for YouTube video assets.
- The persistent `youtube-publishing-log.json` file records `attempted` **before upload**. If uploading fails or the job stops after submitting a video, it **will not auto-retry**: verify YouTube Studio, then reconcile the ledger manually. Successful uploads are recorded with public video links.

## Test before the first scheduled publication

Go to **Actions → Scheduled TheTechnoz YouTube Shorts and Tutorials → Run workflow**.

For a nonpublishing video preview:
- `mode=preview`
- `kind=short` or `kind=tutorial`

Download and watch the MP4 artifact from the workflow. Preview never publishes.

For manual due-day upload choose `mode=publish_due`. Only a currently scheduled, unclaimed video may upload. This is a real **public** upload and is not a test; use only when desired.

## Critical limitations

1. **OAuth External Testing**: Google's refresh tokens for nonbasic scopes may expire after seven days. In Google Auth Platform → Audience, check whether your app is in Testing. If so, migrate to **In production** as Google allows for your own app, follow any required Google verification, and reauthorize locally if necessary. Otherwise upcoming automated uploads may stop.
2. **Content quality**: eSpeak NG is a basic, robotic offline narrator, not a professional neural voice. It is installed automatically for a reliable, cost-free first iteration. Professional voice production requires integrating a properly licensed TTS provider and auditing voice quality. Preview before public releases.
3. **Content policy**: Video scripts are deliberately limited to supported evergreen education and avoid specific unsupported empirical performance claims. The platform can still independently moderate or flag uploads. Mass-produced, repetitive or low-value content may be ineligible for monetization: keep adding original expert commentary, demonstrations and case studies.
4. **Scheduled timing**: GitHub Actions cron can be delayed. Exact-to-the-minute publishing is not guaranteed.
5. **Automatic generation is NOT endless**: 14 unique Shorts and 2 initial tutorials are currently authored. The schedule remains enabled, but skips when original scripts run out.
6. **Don't share credentials**: Secrets `YOUTUBE_CLIENT_SECRET_JSON` and `YOUTUBE_TOKEN_JSON` remain only in GitHub Actions Secrets.

## Source

- `scripts/youtube_editorial.py` — educational scripts and calendar
- `scripts/build_youtube_video.py` — original slides, narration, MP4
- `scripts/youtube_uploader.py` — authorized YouTube API upload
- `.github/workflows/youtube-scheduled.yml` — scheduled renderer/upload with duplicate ledger

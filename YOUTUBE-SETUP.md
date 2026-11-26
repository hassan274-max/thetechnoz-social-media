# YouTube publishing integration (initial safe test)

**Channel intended:** TheTechnoz Solutions. Do not publish until the script reports the correct verified channel.

## Secrets already configured by owner
- `YOUTUBE_CLIENT_SECRET_JSON`: full original OAuth Desktop client JSON from Google Cloud.
- `YOUTUBE_TOKEN_JSON`: full private local `youtube_token.json` authorized for the TheTechnoz Solutions channel.

**Never commit, paste into a chat, or share these credential values.** The `.gitignore` blocks common filenames.

## Step 1 — Test connection only

Open **Actions → Verify YouTube connection and test private Short upload → Run workflow**.
Leave `upload=false`. Run it, then inspect the **Verify authorized channel** job:
- `AUTHORIZED CHANNEL: TheTechnoz Solutions`
- `CHANNEL ID: UC...`
- `SUCCESS: OAuth refresh and YouTube channel lookup succeeded. No upload attempted.`

If this fails with an OAuth `invalid_grant`, check if your OAuth application is still in External Testing mode (seven-day refresh token expiry), and reauthorize locally if needed.

## Step 2 — Optional first upload (PRIVATE, not public)

Only after Step 1 succeeds and you have confirmed the channel ID:
- `upload=true`
- `file=assets/reel-2026-11-26.mp4` (use any existing valid MP4 file in the repository)
- `expected_channel_id=UC...` (copy the verified ID from Step 1)
- `video_title=TheTechnoz Solutions | AI Meets Business #Shorts`
- `privacy=private`

This is a **real YouTube upload**, not a dry run. It will stay private and can be inspected in YouTube Studio. Every new manual upload creates a new video; check Studio before retrying after an uncertain result.

## Longer term

Daily YouTube Shorts production and scheduling are **not yet enabled**. This initial workflow tests authorization and can upload a chosen existing MP4. Our social platform Reels are only 4.8 seconds long; the intended YouTube content strategy is 15–30-second educational Shorts and longer expert videos.

Google OAuth app accounts configured as **External / Testing** issue refresh tokens that expire in around seven days for YouTube scopes. Move to a suitable production or Personal status as supported by Google's account configuration before relying on long-term unattended posting. This is an account/Google configuration change, not a GitHub code change.

The YouTube video upload workflow **never posts to public visibility by default**.

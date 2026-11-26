# Daily social publishing: images + 5-second Reels

## Workflows now installed

- **Prepare daily image and Reel** (09:00 Pakistan time): renders one 1080×1350 educational image and one 720×1280, 4.8-second H.264/AAC MP4 with a subtle zoom animation and a synthesized original musical signature (warm pads, gentle pulse, melodic chimes, and fades). Adds today's two due items to `posts-queue.json`.
- **Publish scheduled Facebook and Instagram posts** (~11:00 Pakistan time): handles image entries.
- **Publish 5-second Reels to Facebook and Instagram** (~19:05 Pakistan time): handles Reel entries via Facebook Reels video upload and Instagram media container.
- **Clean published social assets after 72 hours** (07:00 Pakistan time): deletes eligible source assets from the current branch, leaving social posts intact. Git history will still contain old versions; this does not remove historical storage.

## Verification (important)
1. Open Actions → **Prepare daily image and Reel** → **Run workflow**, select `day_offset=1` to generate tomorrow's content. This will create the first MP4 in GitHub and queue tomorrow's scheduled posts, but **will not publish them immediately**.
2. Confirm files `assets/daily-YYYY-MM-DD.png` and `assets/reel-YYYY-MM-DD.mp4` appear, and `posts-queue.json` has `kind: image` and `kind: reel` entries.
3. Open Actions → **Publish 5-second Reels to Facebook and Instagram** → **Run workflow**, leave `dry_run=true` to verify startup. If tomorrow's Reel isn't due yet, it won't be published.
4. Confirm GitHub secret `META_PAGE_ACCESS_TOKEN` is valid and repository variable `PUBLISHING_ENABLED=true`; no keys belong in source files.
5. At the scheduled time, examine `publishing-log.json` to verify two separate Meta IDs. A green Actions run alone is not proof that a post went public.

## Content and limitations
The automatic content is a **curated 14-topic editorial rotation**, alternating AI/LLMs/automation and Amazon private label/PPC/e-commerce. It is not yet using a live generative AI API, so topical updates, newly announced Amazon changes, bespoke research, and voiceovers are not automatically produced. The Reel is an original moving brand card with a melody synthesized in scripts/original_audio.py from mathematical waveforms; no third-party music samples or commercial recordings are used. This reduces licensing risk but is not a legal guarantee against all copyright claims.

Video upload is dependent on Meta account access, video hosting availability, and Meta's encoding/processing. Never retry a partially successful Reel without checking the destination first to prevent duplicates. Video-based errors are reported in GitHub Actions.

## Relevant GitHub actions
- `.github/workflows/prepare-daily.yml`
- `.github/workflows/publish-meta.yml`
- `.github/workflows/publish-reels.yml`
- `.github/workflows/cleanup-social-assets.yml`

## Google/YouTube
YouTube upload is **not** connected or automated by this implementation.

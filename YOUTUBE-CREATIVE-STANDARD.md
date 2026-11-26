# TheTechnoz Solutions — YouTube Production Standard (approved RAG V3 style)

**Applies to every new educational Short and full-length tutorial, both AI/LLM and Amazon Private Label/PPC.** No legacy slideshow videos, silent reading-heavy screens, robotic eSpeak voice, copied media, or recycled explanations.

## Short: approximately 25–35 seconds, 9:16 full frame

1. **0–5 seconds — practical question / curiosity hook.** Pose a technically meaningful problem ("Why can a RAG answer still be wrong?" or "Why did Amazon PPC spend rise while units stayed flat?").
2. **5–24 seconds — genuinely animated answer.** Demonstrate the process using scene-specific diagrams, moving objects, evidence, timelines, labels, and causal arrows. Never display paragraphs as the main visual. The animation must teach the actual topic rather than simply animate decorative boxes.
3. **24–30 seconds — takeaway plus a closing question when valuable.** A concise, accurate takeaway and a thoughtful prompt to discuss the limitation or next action. Do not tack on a meaningless generic question.

## Sound

- Free open-weight **Kokoro-82M** neural TTS is the default; no paid API.
- Narration must explain what the animation demonstrates and use natural delivery; do not speak verbatim every label.
- Voice louder than original subtle music; duck music during speech; subtle intentional effects only.
- Add readable timed captions; muted viewing must remain intelligible.
- Never fall back to eSpeak or publish without the voice unless the episode is intentionally designed as a music-only promo.

## Technical and editorial requirements

- Original voice, visuals, script, soundtrack and media appropriately licensed for commercial use.
- Verify technical correctness, caveats, claims, examples, and platform-specific PPC terminology.
- For Amazon examples, avoid fabricated datasets or suggestive unsupported performance claims.
- Each episode needs a unique example and unique motion sequence. Merely substituting titles in an identical generic motion graphic **fails** the standard.
- Review visual pacing, legibility, captions, audio quality, voice/music balance, no clipping, ending, and branding.
- Save a private preview artifact first; public publishing only after an explicitly approved template/episode and successful audio/video validation.

## Format-specific notes

- Shorts: vertical 9:16 with centered safe-area content.
- Tutorials: landscape 16:9, deeper demonstration, questions woven naturally through chapters, up to ~5–8 minutes.
- Promotional reels may use music only; educational Shorts should use narration.

## Current automation state (updated)

- **14 Shorts have individually authored educational Q&A motion plans** in `scripts/short_episode_specs.py`; each has its own question, visual processes, conclusion and thoughtful closing question.
- `scripts/render_educational_short.py` renders full-frame original animations from these plans, using free Kokoro neural narration and a custom instrumental mix.
- `scripts/build_youtube_video.py` now routes ALL Shorts to this Q&A renderer; the previous static-slide Short renderer is no longer used.
- `.github/workflows/youtube-scheduled.yml` now installs the narrator, previews the Q&A renderer and **hard-blocks public publishing** at the planning gate.
- **5–8-minute tutorials remain intentionally blocked**, rather than rendering the old rejected slideshow format. They need a dedicated professionally animated long-form renderer before approval.
- **The first GitHub Actions preview and narrated audio must be visually and audibly reviewed.** Source-code integration does not by itself establish that an MP4 successfully rendered or meets the creative bar.
- Publication remains paused until preview and editorial approval. No paid TTS services or API keys are required.

To preview: https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/youtube-scheduled.yml — Run workflow → preview → short. A push to the renderer files also triggers an automatic private preview build.

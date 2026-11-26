# RAG V3 — Natural Narration Integration

The production-ready **voice integration code** is in `scripts/narrate_rag_v3.py`.

## What is included

- Google Cloud Text-to-Speech **Chirp 3 HD** neural voice (`en-US-Chirp3-HD-Charon`).
- Five narration lines synchronized to the 27-second RAG V3 animation:
  - 0.0–4.4s: concern about an unsupported AI answer
  - 4.4–9.1s: document retrieval
  - 9.1–15.0s: passage selection
  - 15.0–21.2s: answer generation using evidence
  - 21.2–27.0s: verify source support
- Original instrumental track attenuated to 13% under narration; voice compression and limiting.
- Exact original V3 video stream is retained without re-encoding.
- Safety: fails if a voice segment runs over its allotted scene by more than the allowed moderate speed adjustment. No truncated sentences.

## Google Cloud setup (not the YouTube OAuth app)

1. In the **same Google Cloud project** as YouTube, enable [Cloud Text-to-Speech API](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com).
2. Make sure Google Cloud billing is set up. This is a usage-based API with potential charges.
3. Create a dedicated identity under [IAM & Admin → Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts). Grant only the permissions needed to invoke Cloud Text-to-Speech (avoid Owner/Editor).
4. For **local** authorization, use the Google Cloud CLI's Application Default Credentials, or a dedicated service account JSON securely stored on your own PC. Never commit credentials.
5. For GitHub Actions, configure a private Actions secret named `GOOGLE_TTS_SERVICE_ACCOUNT_JSON` containing the *complete* service-account JSON. This key method is convenient but should ultimately be replaced with short-lived Workload Identity Federation credentials where possible.
6. Keep the currently paused YouTube auto-publishing workflow paused until the narrated MP4 has been manually reviewed.

## Local usage on Windows

Download the existing **V3 MP4** from the ChatGPT conversation into the extracted repository folder (call it `rag-v3.mp4`).

From PowerShell inside the repository:

```powershell
python -m pip install google-cloud-texttospeech google-auth
python scripts/narrate_rag_v3.py --script-only
```

Google Cloud local ADC option: install Google Cloud CLI, sign in with `gcloud auth application-default login` using an account authorized for the project. If using a downloaded service account key instead, place it outside the public repo and set:

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\outside\the\repo\tts-service-account.json"
```

Once `ffmpeg` and `ffprobe` are installed and accessible from PowerShell, run:

```powershell
python scripts/narrate_rag_v3.py --video rag-v3.mp4 --output rag-v3-narrated.mp4
```

The output has voice and original background music. Listen to it and check caption timing before publishing.

## Current status

**Integration code is written; the natural-voice MP4 has NOT been rendered.** The YouTube OAuth secrets cannot authorize this separate API. Google Text-to-Speech API access and a credential with permission to synthesize speech are required for the final voice generation. The video should not be automatically published until audio and animation are reviewed.

Google voice docs: https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd

# RAG V3 — Free natural neural narration (Kokoro)

The narrator uses **Kokoro-82M (Apache-2.0 model)** through **kokoro-onnx (MIT implementation)**. There are no paid TTS calls, Google Cloud billing requirements, or cloud secrets.

## First test, without publishing

Run GitHub Actions: **Free Kokoro neural voice preview**
`https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/free-kokoro-preview.yml`

Workflow installs the open-source engine and downloads model files from the upstream GitHub Release, generates WAV files for the five RAG scenes and uploads a ZIP artifact for listening. **It does not publish any video**.

## Version 3 integration

`scripts/narrate_rag_v3.py` now accepts:
```
python scripts/narrate_rag_v3.py --video rag-v3.mp4 --output rag-v3-narrated.mp4 --model kokoro-v1.0.onnx --voices-file voices-v1.0.bin
```
Dependencies: `pip install kokoro-onnx soundfile`, FFmpeg/FFprobe, model file and voice pack. Download model files from:
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx`
- `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin`

The source V3 MP4 is not currently in the GitHub repository, so the workflow first validates the voice engine independently. Full MP4 mixing requires making the V3 MP4 available to the build or running this local command on the file downloaded from the ChatGPT conversation.

Narration is placed into five animation scenes. Original music is mixed quieter beneath it. If timing doesn't fit a scene the script stops instead of truncating the speech.

## Current status

Free integration committed; complete narrated MP4 still requires a successful audio preview and a supplied V3 MP4. Publishing remains paused pending creative approval. Check the WAV previews for naturalness, pronunciation (RAG), pacing and commercial suitability before any upload.

Sources: https://huggingface.co/hexgrad/Kokoro-82M and https://github.com/thewh1teagle/kokoro-onnx

## One-step GitHub narrated MP4 workflow

Upload the previously generated V3 MP4 to the repository using **Add file → Upload files** in the `assets` folder and name it **rag-v3.mp4** (repository path `assets/rag-v3.mp4`). The source is the 27-second V3 motion prototype, NOT the earlier static-slide video. If needed, download it from its ChatGPT attachment before uploading.

Then open `https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/rag-v3-kokoro.yml`, click **Run workflow**, and download the `rag-v3-kokoro-narrated-preview` artifact. This builds the fully mixed V3 MP4 with the free neural voice. It does not publish to YouTube.

The main YouTube renderer `scripts/build_youtube_video.py` now uses Kokoro instead of eSpeak too. The old automatic publishing schedule remains paused because its current static-slide visual template has not met the requested professional standard.

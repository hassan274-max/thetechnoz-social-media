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

## Fully automated GitHub render (no user upload required)

The ChatGPT workspace's original video is not directly writable to GitHub as a binary through the current connector. To eliminate manual upload, **scripts/render_rag_v3.py** recreates the full-frame RAG animation from source entirely inside GitHub Actions.

The workflow **Render RAG V3 with free natural Kokoro voice** (in `.github/workflows/rag-v3-kokoro.yml`) starts automatically when the renderer/workflow is committed. It:

1. Installs Pillow, FFmpeg, Kokoro, and soundfile.
2. Downloads the public open-weight model/voices into the temporary runner.
3. Renders the 27-second RAG explainer from code.
4. Synthesizes the five timed neural narration segments.
5. Mixes the narration with original low-volume background music.
6. Uploads `rag-v3-narrated.mp4` as a private GitHub Actions artifact.

Workflow page: https://github.com/hassan274-max/thetechnoz-social-media/actions/workflows/rag-v3-kokoro.yml

**Status:** source and pipeline committed; artifact delivery requires a successful GitHub Actions run. This pipeline does not publish on YouTube. The previous YouTube publishing automation remains paused until visual and narration review.

Note: GitHub renders a reproducible recreation of the V3 animation, not a byte-for-byte copy of the MP4 previously created inside the ChatGPT workspace.

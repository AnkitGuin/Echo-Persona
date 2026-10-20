# Troubleshooting

**`ModuleNotFoundError: streamlit`** — Activate `.venv`, run `pip install -r requirements.txt`, then `streamlit run app.py`.

**No audio in demo mode** — Intentional. No consented demo speaker asset has been distributed. Select `live_local` and install the optional model dependencies to synthesize with a speaker you have permission to use.

**Model package missing** — Use Python 3.11 with `pip install -r requirements-live.txt`. This loads heavyweight PyTorch dependencies and weights; it is not needed for demo or tests.

**CUDA / MPS / RAM / model download failure** — Use `python scripts/check_environment.py`, inspect PyTorch availability, storage and memory. Do not assume CPU can run quickly. `TTS_DEVICE=auto|cpu|cuda|mps` can be set in `.env`. The first generation may require substantial internet download from model hosting.

**Audio cannot be decoded** — Upload 1–30 seconds of clear WAV PCM16, FLAC or OGG; MP3 only where libsndfile supports it. M4A and WebM are not supported by the current parser. Avoid silent/clipped background-heavy recordings.

**Unexpected delivery** — Emotion is a suggestion based on a small phrase lexicon. Use manual override, choose an emotion-labelled reference of the same consenting speaker, listen and compare. Chatterbox `exaggeration` does not guarantee categorical affect.

**Permission failure / profile missing** — The consent statement must be typed exactly. If a file is corrupted, delete/recreate profile after backing up only content the speaker authorized. Check filesystem permissions on local `DATA_DIR`.

**Another device cannot access the app** — Expected, app binds to `127.0.0.1`. Public networking is intentionally unsupported.

# EchoPersona

**Context-Aware Affective Speech Synthesis — a consent-first local expressive TTS application.**

EchoPersona turns user-entered text into synthetic speech conditioned on a voice reference that the user is authorized to use. It can inspect a **user-approved** lightweight conversation-style summary, suggest an intended speaking delivery, and let the user override that suggestion. It compares a neutral baseline against a best-effort conditioned output, **when** local model inference is available. It is experimental, not a medical application, a speaker identity verifier, or an exact voice-reproduction service.

**Current status:** The source and model-independent tests have been implemented; the heavyweight Chatterbox model is **optional and not bundled**. Demo mode deliberately provides a workflow preview **without speech audio** because no consented third-party reference assets are distributed. An opt-in fake **test** mode generates a non-speech sine tone for integration tests.

## Features and honest implementation status

| Feature | Status | Notes |
|---|---|---|
| Streamlit local interface / 6 views | Implemented | No service backend needed |
| Typed permission confirmation | Implemented | User statement, not proof of identity |
| Upload, decode, mono conversion, resample and local voice profiles | Implemented | WAV/FLAC/OGG; MP3 if libsndfile supports it; 1–30 seconds |
| Emotion-labelled reference bank and deletion | Implemented | User assigns the labels |
| TXT/JSON/manual conversation input and editable style summary | Implemented | Heuristic, bounded, no LLM |
| User-approved contextual tone fallback | Implemented | Only a manually approved tone preference; no model context prompts |
| Delivery suggestion with explanation and manual override | Implemented | Basic deterministic keyword rules |
| Live Chatterbox reference-conditioned synthesis | Implemented adapter, **not live-tested** | Optional `chatterbox-tts==0.1.7`; Python 3.11 recommended |
| A/B WAV playback/download and sidecar metadata | Implemented, **requires live model** | Same text/profile; actual waveform depends on model |
| Session-only 1–5 listening ratings | Implemented | Not a population evaluation or benchmark |
| Fake deterministic tone for tests | Implemented | Never portrayed as human speech |
| Transparent no-audio demo mode | Implemented | No model weights downloaded |
| Qwen3-TTS, cloud LLM, ASR and automatic voice enrolment | Not implemented | Out of MVP scope |

## Quick start — Windows PowerShell (Python 3.11)

```powershell
cd EchoPersona
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
python scripts/check_environment.py
streamlit run app.py
```

Open **http://127.0.0.1:8501**. Start in **demo** mode; no downloads of model weights are required. To install the *optional* live model, from that same environment:

```powershell
pip install -r requirements-live.txt
# Optional: edit a local .env to set TTS_DEVICE=cuda if a supported CUDA/PyTorch stack is installed.
streamlit run app.py
```

Choose `live_local` in the sidebar. **First generation** may download hundreds of MB or more of Chatterbox checkpoint data, depending on model version. Confirm your own hardware, PyTorch installation and licensing before proceeding. Installing Chatterbox may need a platform-specific CUDA/PyTorch setup. **The demo and tests do not require a GPU.**

## Quick start — macOS/Linux

```bash
cd EchoPersona
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
python scripts/check_environment.py
streamlit run app.py
```

For optional real TTS, `pip install -r requirements-live.txt` and select `live_local`. CPU or Apple Silicon performance/compatibility are **not guaranteed**; the official Chatterbox repo developed and tested on Python 3.11 / Debian 11. The initial model download needs internet, but audio inference occurs through the local package. This app binds to localhost only (`.streamlit/config.toml`). Do not expose it publicly.

## Usage walkthrough

1. **Start here:** read the disclosure, select demo or live mode.
2. **Voice profiles:** choose your own voice or an adult speaker's explicitly permitted voice; type the permission statement, preview an approximately 5–30s clean speaking sample, then save. Additional recordings from the same speaker can be labelled calm, happy, excited, etc. Unavailable labels fall back visibly to the neutral clip. Audio can be individually removed, except the primary reference (delete the profile to remove that).
3. **Conversation context:** paste text, choose `.txt`, or upload JSON: `[{"role":"user","content":"Hello"}]` or `{ "messages": [...] }`. Review and edit heuristic observations; choose your intended default tone. Save *only the compact edited summary* to your profile if desired. Do not paste other people's private messages without their permission.
4. **Speech studio:** type an English message (up to 1,500 chars), optionally use approved context, inspect suggested delivery, adjust override/intensity, and generate neutral / chosen / compare both in live mode. Listen, review metadata, download WAV and the synthetic-audio provenance JSON. In demo mode these generation buttons are correctly disabled.
5. **Compare & evaluate:** inspect paired results for the same text and profile. Rate intelligibility, naturalness, voice resemblance, intended tone and preference from 1 to 5. Ratings exist only in your Streamlit session.
6. **Privacy & data:** clear generations, context, references, profiles, or all profiles using deliberate confirmation. The app cannot erase copies, backups or OS-level caches.

**Demo flow for a 2–3 minute presentation:** show the consent gate, save a consenting speaker reference, import a hand-written synthetic conversation, review a summary, select an emotion, and explain the demo/live difference. On a live-capable machine, compare outputs and download the WAV. Open Privacy & data and delete the profile. Never pretend demo mode actually cloned a voice.

## Model strategy and limitations

- Engine: Resemble AI's **original English Chatterbox TTS**, behind a `TTSBackend` protocol. It accepts `audio_prompt_path`, `exaggeration` and `cfg_weight`; the latest upstream repository also documents Turbo, Nano and multilingual V3, but this MVP deliberately integrates the original English model for its documented expressiveness controls.
- Best-effort intensity `i∈[0,1]` maps to exaggeration `0.4+0.35i`; the neutral baseline uses `0.5`. Both use `cfg_weight=0.5`. These are **model expressive controls, not sadness/happiness sliders**. User-labelled emotion reference selection may alter performance but cannot guarantee its emotion transfers.
- Context influences the initial suggested tone **only through user-approved fallback preferences**, not through model cross-attention or prompt engineering. When lexical cues exist they can override the fallback unless the user manually overrides everything. The model receives the original text and chosen audio reference, not the raw conversation export.
- The Chatterbox backend may change installed upstream behavior. It is lazily imported/loaded; errors surface in the UI. Official upstream documentation says Chatterbox incorporates PerTh watermarking. **This application does not strip audio watermarks**; it exports the generated waveform as WAV.
- No medical/clinical claims, calibrated emotion probabilities, objective identity matching, synthetic speech guarantee, latency promise, cross-language support (in this original backend), multi-user isolation, or production security review.

## Testing and evaluation

```bash
python -m pytest -q
python -m compileall -q app.py src scripts tests
python scripts/check_environment.py
# opt-in only, after consent and an actual saved profile:
python scripts/check_environment.py --live-tts --profile-id YOUR_PROFILE_ID
# optional ratings summary from participant-collected CSV:
python scripts/summarize_ratings.py docs/ratings_template.csv
```

The live smoke test requires the model to be locally installed, the user's explicitly consented profile ID, and adequate hardware. It does **not** write or log generated speech. Run a manual browser acceptance checklist from `docs/EVALUATION_PROTOCOL.md` on your own setup. No fabricated participant data or scores are included.

## Privacy and responsible use

Profiles and reference WAVs are stored under the local `DATA_DIR/profiles/<random-id>/`. JSON stores declared consent, a transcript only if supplied, and an optional approved compact style summary. Raw conversation logs are not saved by the storage layer. Audio generations are session-only. No paid or cloud LLM service is used; a **first model download** may contact the upstream model host (Hugging Face). Imported source material should not contain another person's private messages without their permission. Streamlit browser and server session memory may temporarily retain texts until reset; the interface provides cleanup controls for the generated metadata and style summary. Ordinary file deletion is not a certified secure wipe.

The app has no login; it is designed for **a single trusted user on localhost**, not public hosting or compliance-critical voice banking. Generated speech is explicitly AI-generated. Do not clone a voice without the adult speaker’s permission, mislead listeners, bypass voice authentication, or create false evidence.

## Architecture, licenses and next steps

See `docs/ARCHITECTURE.md`, `docs/MODEL_NOTES.md`, `docs/PRIVACY_AND_SAFETY.md`, `docs/EVALUATION_PROTOCOL.md`, `docs/TROUBLESHOOTING.md` and `THIRD_PARTY_NOTICES.md`.

Future priorities: separately test the Chatterbox local inference path on Python 3.11 with a consenting reference; verify CUDA/MPS paths and memory behavior; user-test the baseline versus manual versus context-assisted options; improve explicit-context influence, accessibility, audio format diagnostics and model version reproducibility. A Qwen3-TTS adapter remains optional and must not assume unsupported instructions on Base clone checkpoints.

### Attribution

Resemble AI, *Chatterbox-TTS* (2025), https://github.com/resemble-ai/chatterbox . The Chatterbox code repository and `ResembleAI/chatterbox` checkpoint list MIT licensing as of 2026-10-20; confirm current terms before deployment. **No model weights or third-party recordings are included in this source ZIP.**

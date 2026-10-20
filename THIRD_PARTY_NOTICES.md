# Third-party notices (verified sources as of 2026-10-20)

No checkpoint weights, other-party voice recordings, example voice clips, or pre-generated third-party speech samples are redistributed here.

| Component | Source | Version / checkpoint | License | Use / restrictions |
|---|---|---|---|---|
| Chatterbox TTS code | https://github.com/resemble-ai/chatterbox | PyPI `chatterbox-tts==0.1.7` | MIT according to official repository/PyPI | Optional runtime; not bundled with ZIP; inspect transitive dependency licenses |
| Original Chatterbox checkpoint | https://huggingface.co/ResembleAI/chatterbox | `ResembleAI/chatterbox` (unpinned hosted revision) | MIT according to model card | Downloaded by local runtime when activated, **not bundled**; verify exact revision/license when deploying |
| Streamlit | https://github.com/streamlit/streamlit | 1.51.0 | Apache-2.0 | Local web UI |
| NumPy | https://numpy.org | >=1.26,<3 | BSD-3-Clause | Audio arrays |
| SciPy | https://scipy.org | >=1.12,<2 | BSD-3-Clause | Polyphase resampling |
| SoundFile / libsndfile | https://python-soundfile.readthedocs.io/ | >=0.12.1,<0.14 | BSD-3-Clause / LGPL-2.1-or-later (respect included libsndfile terms) | Audio decoding/encoding; supported codecs vary |
| python-dotenv | https://github.com/theskumar/python-dotenv | >=1,<2 | BSD-3-Clause | Local optional configuration |
| pytest | https://pytest.org | >=8,<10 | MIT | Development tests only |

Resemble AI also reports built-in PerTh audio watermarks in Chatterbox. This app does not try to remove them. Each locally generated audio output receives visible AI-generated provenance and offers a sidecar metadata JSON file. License information should be re-verified for all production uses, especially checkpoint model revisions.

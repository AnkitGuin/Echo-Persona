# Model integration notes (2026-10-20)

**Chosen adapter:** original English `ChatterboxTTS` from PyPI `chatterbox-tts==0.1.7`, rather than the newer Turbo/Nano/V3 family, because the spec calls for `exaggeration`/`cfg_weight` controls. This is a deliberately narrow implementation.

Verified official resources:

- https://github.com/resemble-ai/chatterbox
- https://github.com/resemble-ai/chatterbox/blob/master/src/chatterbox/tts.py
- https://github.com/resemble-ai/chatterbox/blob/master/example_tts.py
- https://pypi.org/project/chatterbox-tts/
- https://huggingface.co/ResembleAI/chatterbox

API form:

```python
from chatterbox.tts import ChatterboxTTS
model = ChatterboxTTS.from_pretrained(device='cuda')
wave = model.generate(text, audio_prompt_path='/path/to/consented.wav',
                      exaggeration=0.5, cfg_weight=0.5)
sample_rate = model.sr
```

The app loads at *first* real synthesis, not on launch. Reference paths are created by the profile store and not taken directly from the browser. `exaggeration` is neither a universal emotion label nor reliable emotion intensity. Reference-conditioned emotional consistency, speaker similarity and latency require empirical testing. Users preview output and may compare neutral and conditioned variants. The adapter does not train a model, strip watermarks, expose undocumented arguments or support arbitrary prompt injection into the model.

**Unverified:** the exact behavior and hardware success of `chatterbox-tts==0.1.7` on users' machines. The CI/test suite deliberately avoids loading model weights. The upstream repo reports development/testing on Python 3.11 / Debian 11. Model code and referenced checkpoint list MIT licensing on their official pages; reconfirm for intended uses and checkpoint revisions. Model weights are not stored in the project or archive.

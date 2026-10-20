"""Lazy, offline-once-downloaded English voice-conditioned Chatterbox adapter.

Checked against resemble-ai/chatterbox docs and ChatterboxTTS.generate API.
Never import heavyweight packages on app launch.
"""
from io import BytesIO
import importlib.util
import numpy as np
import soundfile as sf
from ..models import SynthesisRequest
from .base import BackendOutput


def map_expressiveness(intensity: float, neutral=False) -> dict[str,float]:
    if not 0 <= intensity <= 1: raise ValueError('Intensity outside [0,1].')
    # The scalar is expressiveness, NOT a per-emotion strength value.
    return {'exaggeration':0.5 if neutral else round(0.4 + 0.35*intensity,3),
            'cfg_weight':0.5}

class ChatterboxBackend:
    name='Chatterbox original English (local)'
    def __init__(self,device='auto'):
        self.device=device; self.model=None

    def health_check(self):
        return ('Chatterbox package installed (weights loaded only on demand).'
                if importlib.util.find_spec('chatterbox') else
                'chatterbox-tts not installed; use requirements-live.txt for optional live inference.')

    def load(self):
        if self.model is not None: return
        try:
            import torch
            from chatterbox.tts import ChatterboxTTS
        except ImportError as exc:
            raise RuntimeError('Missing Chatterbox dependency. Install requirements-live.txt in Python 3.11.') from exc
        device=self.device
        if device=='auto': device='cuda' if torch.cuda.is_available() else 'mps' if hasattr(torch.backends,'mps') and torch.backends.mps.is_available() else 'cpu'
        try: self.model=ChatterboxTTS.from_pretrained(device=device)
        except Exception as exc:
            raise RuntimeError(f'Could not load Chatterbox on {device}. Check model download, memory and runtime compatibility.') from exc

    def synthesize(self,request:SynthesisRequest) -> BackendOutput:
        if request.language!='en': raise ValueError('The configured Chatterbox original backend supports English only.')
        if set(request.controls) - {'exaggeration','cfg_weight'}:
            raise ValueError('Unsupported Chatterbox control requested.')
        if not request.reference_path: raise ValueError('A consenting speaker reference is required.')
        self.load()
        try:
            wave=self.model.generate(request.text, audio_prompt_path=request.reference_path, **request.controls)
            signal=wave.detach().cpu().float().numpy().squeeze()
            if signal.ndim != 1 or not np.isfinite(signal).all() or len(signal)==0:
                raise ValueError('Model returned invalid audio.')
            output=BytesIO()
            # Preserve watermark: no DSP except WAV serialization.
            sf.write(output,signal,int(self.model.sr),format='WAV',subtype='PCM_16')
            return BackendOutput(output.getvalue(),int(self.model.sr))
        except (RuntimeError,ValueError): raise
        except Exception as exc: raise RuntimeError('Chatterbox inference failed; see setup and troubleshooting guidance.') from exc

    def unload(self):
        self.model=None

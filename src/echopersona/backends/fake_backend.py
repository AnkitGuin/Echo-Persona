"""Test-only deterministic synthetic tone; never used as mocked human speech."""
from io import BytesIO
import numpy as np
import soundfile as sf
from ..models import SynthesisRequest
from .base import BackendOutput

class FakeBackend:
    name='Fake test tone (never speech)'
    def health_check(self): return 'Test fixture ready.'
    def load(self): pass
    def synthesize(self,request:SynthesisRequest) -> BackendOutput:
        sr=16000; t=np.arange(sr//4,dtype=np.float32)/sr
        samples=0.15*np.sin(2*np.pi*440*t)
        out=BytesIO(); sf.write(out,samples,sr,format='WAV')
        return BackendOutput(out.getvalue(),sr)
    def unload(self): pass

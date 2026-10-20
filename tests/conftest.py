from io import BytesIO
import numpy as np
import pytest
import soundfile as sf
from echopersona.audio.validation import check_reference

@pytest.fixture
def sample_wav():
    sr=24000
    t=np.arange(sr*3,dtype=np.float32)/sr
    signal=0.1*np.sin(2*np.pi*400*t)
    out=BytesIO(); sf.write(out,signal,sr,format='WAV')
    return out.getvalue()

@pytest.fixture
def sample_check(sample_wav):
    return check_reference(sample_wav,'synthetic.wav')

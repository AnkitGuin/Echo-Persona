import pytest
from io import BytesIO
import numpy as np
import soundfile as sf
from echopersona.audio.validation import check_reference,validate_output

def test_valid_synthetic(sample_wav):
    check=check_reference(sample_wav,'fixture.wav')
    assert check.duration==3
    assert validate_output(check.wav_bytes)[0]==24000

def test_invalid_audio():
    with pytest.raises(ValueError): check_reference(b'bad','fake.exe')
    with pytest.raises(ValueError): check_reference(b'garbage','fake.wav')
    with pytest.raises(ValueError): check_reference(b'','empty.wav')

def test_max_size(sample_wav):
    with pytest.raises(ValueError): check_reference(sample_wav,'s.wav',max_mb=0)

def test_antiphase_stereo_keeps_speech_channel():
    sr=24000
    t=np.arange(sr,dtype=np.float32)/sr
    mono=0.1*np.sin(2*np.pi*300*t)
    stereo=np.column_stack((mono,-mono))
    out=BytesIO(); sf.write(out,stereo,sr,format='WAV')
    checked=check_reference(out.getvalue(),'stereo.wav')
    assert checked.peak > 0.09
    assert any('strongest channel was retained' in warning for warning in checked.warnings)

def test_rejects_unsupported_output_rate():
    out=BytesIO(); sf.write(out,np.ones(100,dtype=np.float32)*0.1,1000,format='WAV')
    with pytest.raises(ValueError,match='unsupported sample rate'):
        validate_output(out.getvalue())

import pytest
from echopersona.backends.fake_backend import FakeBackend
from echopersona.services.generation import generate
from echopersona.storage.local_store import ProfileStore
from echopersona.models import CONSENT_PHRASE

def test_generation_validated(tmp_path,sample_check):
    s=ProfileStore(tmp_path)
    p=s.create('Me','own_voice',CONSENT_PHRASE,sample_check.wav_bytes,sample_check)
    r=generate(s,FakeBackend(),p['profile_id'],'Hello','happy',.5,'test')
    assert r.audio_bytes is not None and r.duration_seconds>0
    assert r.reference_label=='neutral'
    assert 'audio_bytes' not in r.metadata()
    assert 'artificial tone' in ' '.join(r.warnings)
    with pytest.raises(ValueError): generate(s,FakeBackend(),p['profile_id'],'   ','happy',.5,'test')
    with pytest.raises(ValueError): generate(s,FakeBackend(),p['profile_id'],'X'*1501,'happy',.5,'test')
    with pytest.raises(ValueError): generate(s,FakeBackend(),p['profile_id'],'Hello','happy',.5,'demo')

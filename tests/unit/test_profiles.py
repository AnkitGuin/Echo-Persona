import pytest
from echopersona.storage.local_store import ProfileStore
from echopersona.models import CONSENT_PHRASE

def test_round_trip_consent_delete(tmp_path,sample_check):
    s=ProfileStore(tmp_path)
    with pytest.raises(PermissionError):
        s.create('Name','own_voice','no',sample_check.wav_bytes,sample_check)
    p=s.create('My voice','own_voice',CONSENT_PHRASE,sample_check.wav_bytes,sample_check)
    pid=p['profile_id']
    assert s.load(pid)['display_name']=='My voice'
    assert s.reference(pid,'neutral')[1]=='neutral'
    assert s.reference(pid,'excited')[1]=='neutral'
    s.add_reference(pid,'excited',sample_check.wav_bytes,sample_check)
    assert s.reference(pid,'excited')[1]=='excited'
    s.remove_reference(pid,'excited')
    assert s.reference(pid,'excited')[1]=='neutral'
    s.save_preferences(pid,{'tone':'calm','private_conversation':'never persist'})
    assert 'private_conversation' not in s.load(pid)['communication_preferences']
    assert s.delete(pid)
    assert not s.delete(pid)
    with pytest.raises(ValueError): s.load(pid)

def test_invalid_ids(tmp_path):
    s=ProfileStore(tmp_path)
    for path in ('../../root','other','0'*31+'x'):
        with pytest.raises(ValueError): s.directory(path)

def test_corrupt_json(tmp_path):
    s=ProfileStore(tmp_path)
    pid='f'*32
    d=s.directory(pid);d.mkdir()
    (d/'profile.json').write_text('{broken',encoding='utf-8')
    with pytest.raises(ValueError): s.load(pid)

def test_delete_all_removes_corrupt_profiles(tmp_path):
    s=ProfileStore(tmp_path)
    corrupt=s.root/('f'*32)
    corrupt.mkdir()
    (corrupt/'profile.json').write_text('{broken',encoding='utf-8')
    s.delete_all()
    assert list(s.root.iterdir())==[]

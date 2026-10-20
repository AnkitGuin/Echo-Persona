from echopersona.storage.local_store import ProfileStore
from echopersona.models import CONSENT_PHRASE
from echopersona.services.context import extract_context,summarize
from echopersona.services.emotion import plan
from echopersona.services.generation import generate
from echopersona.backends.fake_backend import FakeBackend

def test_end_to_end_without_model(tmp_path,sample_check):
    store=ProfileStore(tmp_path)
    profile=store.create('Me','own_voice',CONSENT_PHRASE,sample_check.wav_bytes,sample_check)
    context=extract_context('[{"role":"user","content":"Thanks for your help."}]','json')
    prefs=summarize(context)
    prefs['tone']='warm_reassuring'
    store.save_preferences(profile['profile_id'],prefs)
    suggestion=plan('Here is the report.',context=prefs)
    assert suggestion.label=='warm_reassuring'
    gen=generate(store,FakeBackend(),profile['profile_id'],'Here is the report.',suggestion.label,0.5,'test')
    assert gen.duration_seconds>0
    assert gen.mode=='test'
    assert store.delete(profile['profile_id'])
    assert not store.list_profiles()

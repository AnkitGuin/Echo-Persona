"""Request validation, reference matching, conditioning and verified audio output."""
from time import perf_counter
from ..audio.validation import validate_output
from ..models import SynthesisRequest,SynthesisResult,DELIVERIES
from ..backends.chatterbox_backend import map_expressiveness


def generate(store,backend,profile_id,text,delivery,intensity,mode,max_chars=1500):
    if mode not in {'live_local','test'}: raise ValueError('Demo mode does not synthesize audio.')
    if not isinstance(text,str) or not text.strip() or len(text)>max_chars:
        raise ValueError(f'Enter 1–{max_chars} characters of non-empty text.')
    if delivery not in DELIVERIES: raise ValueError('Unknown delivery label.')
    if not 0<=intensity<=1: raise ValueError('Intensity outside [0, 1].')
    p=store.load(profile_id)
    if not p['consent_confirmed']: raise PermissionError('Consent is required.')
    ref_path,ref_label=store.reference(profile_id,delivery)
    warnings=[]
    if ref_label!=delivery:
        warnings.append(f'No {delivery.replace("_"," ")} reference; using the neutral recording instead.')
    if mode=='test':
        controls={}; warnings.append('Test fixture: this audio is an artificial tone, not synthesized speech.')
    else:
        controls=map_expressiveness(intensity,neutral=delivery=='neutral')
        warnings.append('Expressiveness is not categorical emotion control. Preview the output.')
    start=perf_counter()
    result=backend.synthesize(SynthesisRequest(text=text,reference_path=ref_path,controls=controls))
    sr,duration=validate_output(result.wav_bytes)
    return SynthesisResult(audio_bytes=result.wav_bytes,sample_rate=sr,duration_seconds=duration,
            backend=backend.name,mode=mode,delivery=delivery,reference_label=ref_label,
            controls=controls,warnings=warnings,elapsed_seconds=round(perf_counter()-start,3))

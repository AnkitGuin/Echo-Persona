"""Environment diagnostics; an opt-in live smoke test requires an explicit saved profile."""
import argparse
import importlib.util
import platform
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from echopersona.config import Settings
from echopersona.storage.local_store import ProfileStore
from echopersona.backends.chatterbox_backend import ChatterboxBackend
from echopersona.services.generation import generate

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--live-tts',action='store_true',help='Explicitly load large model weights and synthesize')
    parser.add_argument('--profile-id',help='Your consenting locally saved profile ID; required for live mode')
    args=parser.parse_args()
    s=Settings.from_env()
    print('EchoPersona runtime diagnostics')
    print('Python',platform.python_version(),'OS',platform.platform())
    print('Mode',s.mode,'device setting',s.device)
    print('Chatterbox installed?',bool(importlib.util.find_spec('chatterbox')))
    print('Model weights are never downloaded by ordinary diagnostics.')
    if not args.live_tts:
        print('Next: streamlit run app.py (demo mode), or opt in with --live-tts --profile-id ID')
        return 0
    if not args.profile_id:
        parser.error('--live-tts requires --profile-id for a consent-confirmed locally saved voice')
    print('Opt-in live inference: the installed model may download large weights. Audio stays local for model inference.')
    try:
        result=generate(ProfileStore(s.data_dir),ChatterboxBackend(s.device),args.profile_id,
            'This is an experimental synthetic speech test.', 'neutral',0.5,'live_local',s.max_text_chars)
    except Exception as exc:
        print('Live smoke test FAILED:',str(exc))
        return 1
    print('Live smoke test PASS. Samples validated. Duration:',round(result.duration_seconds,2),
          'Inference seconds:',result.elapsed_seconds, 'Backend:',result.backend)
    print('Output was not saved; transcript/audio not logged.')
    return 0

if __name__=='__main__': raise SystemExit(main())

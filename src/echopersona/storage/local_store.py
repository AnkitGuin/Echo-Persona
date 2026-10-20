"""Local-only profiles with validated paths, atomic JSON and deliberate deletion."""
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from ..models import now, uid, CONSENT_PHRASE, REF_LABELS

ID_RE = re.compile(r'^[0-9a-f]{32}$')

class ProfileStore:
    def __init__(self, data_dir):
        self.root = Path(data_dir).expanduser().resolve() / 'profiles'
        self.root.mkdir(parents=True,exist_ok=True)

    def directory(self, profile_id):
        if not isinstance(profile_id,str) or not ID_RE.fullmatch(profile_id):
            raise ValueError('Invalid profile ID')
        folder = self.root / profile_id
        # Reject symlinked profile folders or any root escape.
        if folder.is_symlink() or not folder.resolve().is_relative_to(self.root.resolve()):
            raise ValueError('Profile path outside data directory')
        return folder

    @staticmethod
    def _atomic_json(path, data):
        fd, tmp = tempfile.mkstemp(prefix='.pending-',dir=str(path.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=2)
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def create(self, name, consent_scope, confirmation, normalized_wav: bytes, details, transcript=''):
        if consent_scope not in {'own_voice','authorized_adult_voice'} or confirmation != CONSENT_PHRASE:
            raise PermissionError('Explicit speaker permission must be acknowledged first.')
        if not normalized_wav: raise ValueError('Valid reference audio is required.')
        pid=uid(); folder=self.directory(pid); refs=folder/'references'
        refs.mkdir(parents=True,exist_ok=False)
        try:
            (refs/'neutral.wav').write_bytes(normalized_wav)
            p = {'profile_id':pid,'display_name':str(name).strip()[:80] or 'My voice',
                 'created_at':now(),'consent_confirmed':True,'consent_scope':consent_scope,
                 'consent_notice_version':'1.0','primary_reference_path':'references/neutral.wav',
                 'primary_reference_transcript':str(transcript)[:400] or None,
                 'emotion_references':{'neutral':{'relative_path':'references/neutral.wav',
                     'label':'neutral','duration_seconds':details.duration,
                     'sample_rate_hz':24000,'user_labelled':True,'created_at':now(),
                     'processing_warnings':details.warnings}},'communication_preferences':{},'summary_version':1}
            self._atomic_json(folder/'profile.json',p)
        except Exception:
            shutil.rmtree(folder,ignore_errors=True)
            raise
        return p

    def load(self, pid):
        folder=self.directory(pid)
        try:
            with (folder/'profile.json').open(encoding='utf-8') as f: data=json.load(f)
        except (OSError,ValueError) as exc: raise ValueError('Profile is missing or its metadata is corrupted.') from exc
        if not isinstance(data,dict) or data.get('profile_id') != pid or not data.get('consent_confirmed'):
            raise PermissionError('Profile metadata or consent is invalid.')
        if not isinstance(data.get('emotion_references'),dict) or 'neutral' not in data['emotion_references']:
            raise ValueError('Profile references are missing or corrupted.')
        return data

    def list_profiles(self):
        result=[]
        for folder in self.root.iterdir():
            if folder.is_dir() and not folder.is_symlink() and ID_RE.fullmatch(folder.name):
                try: result.append(self.load(folder.name))
                except (ValueError,PermissionError): continue
        return sorted(result,key=lambda p:p['created_at'],reverse=True)

    def reference(self,pid,label):
        p=self.load(pid)
        if label not in REF_LABELS: raise ValueError('Invalid emotion reference label')
        refs=p['emotion_references']
        used=label if label in refs else 'neutral'
        relative=refs[used]['relative_path']
        folder=self.directory(pid)
        raw=folder/relative
        path=raw.resolve()
        if raw.is_symlink() or not path.is_relative_to(folder.resolve()) or not path.is_file():
            raise ValueError('Reference file is missing or is outside profile storage.')
        return str(path),used

    def add_reference(self,pid,label,wav,details,transcript=''):
        if label not in REF_LABELS or label=='neutral': raise ValueError('Select a non-neutral delivery label.')
        p=self.load(pid); folder=self.directory(pid)
        target=folder/'references'/f'{label}.wav'
        if target.is_symlink(): raise ValueError('Unsafe reference path')
        with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.audio-',delete=False) as f:
            tmp=f.name; f.write(wav)
        try: os.replace(tmp,target)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
        p['emotion_references'][label]={'relative_path':f'references/{label}.wav','label':label,
          'duration_seconds':details.duration,'sample_rate_hz':24000,'created_at':now(),
          'user_labelled':True,'transcript':str(transcript)[:400] or None,
          'processing_warnings':details.warnings}
        self._atomic_json(folder/'profile.json',p)
        return p

    def remove_reference(self,pid,label):
        if label=='neutral' or label not in REF_LABELS: raise ValueError('Primary clip cannot be removed separately.')
        p=self.load(pid)
        if label in p['emotion_references']:
            file,actual=self.reference(pid,label)
            Path(file).unlink()
            del p['emotion_references'][label]
            self._atomic_json(self.directory(pid)/'profile.json',p)

    def save_preferences(self,pid,preferences):
        p=self.load(pid)
        # Approved compact fields only; no raw conversation dump.
        allow={'language','sentence_length','formality','tone','greetings','punctuation'}
        p['communication_preferences']={k:str(v)[:140] for k,v in preferences.items() if k in allow}
        self._atomic_json(self.directory(pid)/'profile.json',p)
        return p

    def delete(self,pid):
        folder=self.directory(pid)
        if not folder.exists(): return False
        shutil.rmtree(folder)
        return True

    def delete_all(self):
        # Include unreadable/corrupt profile folders too; list_profiles() is
        # intentionally user-facing and skips invalid records, but a deliberate
        # "delete all" must not leave those records behind.
        for entry in self.root.iterdir():
            if entry.is_symlink() or not entry.is_dir():
                entry.unlink()
            else:
                shutil.rmtree(entry)

"""Typed, privacy-preserving local application configuration."""
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    app_name: str = 'EchoPersona'
    mode: str = 'demo'
    data_dir: Path = Path('./data')
    device: str = 'auto'
    max_upload_mb: int = 25
    max_reference_seconds: int = 30
    max_text_chars: int = 1500
    save_history: bool = False
    
    @classmethod
    def from_env(cls):
        mode = os.getenv('APP_MODE', 'demo').lower()
        if mode not in {'demo', 'live_local', 'test'}:
            raise ValueError('APP_MODE must be demo, live_local, or test')
        device = os.getenv('TTS_DEVICE','auto').lower()
        if device not in {'auto','cuda','cpu','mps'}:
            raise ValueError('TTS_DEVICE must be auto, cuda, cpu, or mps')
        max_upload_mb=int(os.getenv('MAX_UPLOAD_MB',25))
        max_reference_seconds=int(os.getenv('MAX_REFERENCE_SECONDS',30))
        max_text_chars=int(os.getenv('MAX_TEXT_CHARS',1500))
        if max_upload_mb < 1 or max_reference_seconds < 1 or max_text_chars < 1:
            raise ValueError('MAX_UPLOAD_MB, MAX_REFERENCE_SECONDS, and MAX_TEXT_CHARS must be positive integers.')
        return cls(
            app_name=os.getenv('APP_NAME','EchoPersona'), mode=mode,
            data_dir=Path(os.getenv('DATA_DIR','./data')).expanduser().resolve(),
            device=device, max_upload_mb=max_upload_mb,
            max_reference_seconds=max_reference_seconds,
            max_text_chars=max_text_chars,
            save_history=os.getenv('SAVE_GENERATION_HISTORY','false').lower() == 'true',
        )

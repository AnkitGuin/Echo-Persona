"""Pure domain contracts; no Streamlit and no model dependencies."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

DELIVERIES = ('neutral','calm','warm_reassuring','happy','sad_reflective','concerned','excited')
REF_LABELS = ('neutral','calm','happy','sad_reflective','concerned','warm_reassuring','excited')
CONSENT_PHRASE = 'I HAVE PERMISSION TO USE THIS VOICE'

def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return uuid4().hex

@dataclass
class EmotionPlan:
    label: str
    intensity: float
    confidence: str
    explanation: str
    warnings: list[str] = field(default_factory=list)
    def __post_init__(self):
        if self.label not in DELIVERIES: raise ValueError('Unsupported delivery')
        if not 0 <= self.intensity <= 1: raise ValueError('Intensity must be between 0 and 1')

@dataclass
class SynthesisRequest:
    text: str
    reference_path: str
    language: str = 'en'
    controls: dict[str, Any] = field(default_factory=dict)

@dataclass
class SynthesisResult:
    audio_bytes: bytes | None
    sample_rate: int | None
    duration_seconds: float | None
    backend: str
    mode: str
    delivery: str
    reference_label: str
    controls: dict[str, Any]
    warnings: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    generated_at: str = field(default_factory=now)
    generation_id: str = field(default_factory=uid)
    provenance: str = 'AI-generated synthetic speech; not an authentic recording.'
    def metadata(self):
        d = asdict(self)
        d.pop('audio_bytes',None)
        return d

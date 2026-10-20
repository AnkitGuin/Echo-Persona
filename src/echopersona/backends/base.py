from typing import Protocol
from dataclasses import dataclass
from ..models import SynthesisRequest

@dataclass
class BackendOutput:
    wav_bytes: bytes
    sample_rate: int

class TTSBackend(Protocol):
    name: str
    def health_check(self) -> str: ...
    def load(self) -> None: ...
    def synthesize(self, request: SynthesisRequest) -> BackendOutput: ...
    def unload(self) -> None: ...

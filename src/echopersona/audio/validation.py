"""Decode and normalize bounded reference uploads. Decoder support varies by OS."""
from dataclasses import dataclass
from io import BytesIO
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from math import gcd

@dataclass
class AudioCheck:
    wav_bytes: bytes
    duration: float
    original_sample_rate: int
    channels: int
    silence_fraction: float
    peak: float
    warnings: list[str]


def check_reference(data: bytes, filename: str, max_mb=25, max_seconds=30, target_rate=24000) -> AudioCheck:
    if not data: raise ValueError('The selected audio file is empty.')
    if len(data) > max_mb * 1024 * 1024: raise ValueError(f'Audio exceeds {max_mb} MB.')
    ext = filename.rsplit('.',1)[-1].lower() if '.' in filename else ''
    if ext not in {'wav','flac','ogg','mp3'}:
        raise ValueError('Use WAV, FLAC, OGG or decoder-supported MP3 audio.')
    try:
        arr, sr = sf.read(BytesIO(data), dtype='float32', always_2d=True)
    except Exception as exc:
        raise ValueError('Unable to decode this recording. Convert it to PCM WAV and retry.') from exc
    if not 8000 <= sr <= 192000 or arr.shape[1] > 8: raise ValueError('Unsupported sample rate or channel count.')
    duration = len(arr) / sr
    if not 1.0 <= duration <= max_seconds:
        raise ValueError(f'Reference must be 1–{max_seconds} seconds; received {duration:.1f}.')
    if not np.all(np.isfinite(arr)): raise ValueError('Recording contains invalid samples.')
    original_channels = arr.shape[1]
    channel_peaks = np.max(np.abs(arr), axis=0)
    # Averaging stereo is normally appropriate, but opposing microphone
    # polarity can cancel speech almost completely. In that case keep the
    # cleanest (highest-RMS) channel instead of saving near-silence.
    mono = arr.mean(axis=1)
    channel_rms = np.sqrt(np.mean(arr.astype(np.float64) ** 2, axis=0))
    mono_rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2)))
    strongest_channel = int(np.argmax(channel_rms))
    used_single_channel = (channel_rms[strongest_channel] > 0 and
                           mono_rms < 0.25 * channel_rms[strongest_channel])
    if used_single_channel:
        mono = arr[:, strongest_channel]
    peak = float(np.max(np.abs(mono)))
    rms = float(np.sqrt(np.mean(mono.astype(np.float64)**2)))
    if rms < 0.001: raise ValueError('The recording is silent or nearly silent.')
    warnings = []
    if original_channels > 1: warnings.append('Stereo or multichannel audio was mixed to mono.')
    if used_single_channel:
        warnings.append('Channels nearly cancelled when mixed; the strongest channel was retained.')
    if np.any(channel_peaks >= 0.999): warnings.append('Recording may contain clipped peaks.')
    silence_fraction = float(np.mean(np.abs(mono) < 0.003))
    if silence_fraction > 0.7: warnings.append('Many samples are near-silent; use clean continuous speech.')
    if sr != target_rate:
        divisor = gcd(sr,target_rate)
        mono = resample_poly(mono, target_rate//divisor, sr//divisor).astype(np.float32)
    mono = np.clip(mono,-1,1)
    out = BytesIO()
    sf.write(out,mono,target_rate,format='WAV', subtype='PCM_16')
    return AudioCheck(out.getvalue(),duration,sr,original_channels,silence_fraction,peak,warnings)


def validate_output(data: bytes) -> tuple[int,float]:
    try:
        arr,sr = sf.read(BytesIO(data),dtype='float32')
    except Exception as exc:
        raise ValueError('The model returned unreadable audio.') from exc
    if not 8000 <= sr <= 192000 or arr.ndim not in (1, 2) or (arr.ndim == 2 and arr.shape[1] > 8):
        raise ValueError('The model returned audio with an unsupported sample rate or channel count.')
    if len(arr)==0 or not np.all(np.isfinite(arr)) or float(np.max(np.abs(arr))) < 0.000001:
        raise ValueError('The model returned an empty or silent waveform.')
    return sr, len(arr)/sr

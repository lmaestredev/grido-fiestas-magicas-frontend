"""
Providers module for TTS, lip-sync, and video generation.
"""

from .base import TTSProvider, LipsyncProvider, VideoProvider
from .kokoro_tts import KokoroTTSProvider
from .elevenlabs_tts import ElevenLabsTTSProvider
from .wav2lip_lipsync import Wav2LipLipsyncProvider
from .synclabs_lipsync import SyncLabsLipsyncProvider
from .heygen_video import HeyGenVideoProvider
from .did_video import DIDVideoProvider
from .higgsfield_video import HiggsfieldVideoProvider
from .manager import ProviderManager

__all__ = [
    "TTSProvider",
    "LipsyncProvider",
    "VideoProvider",
    "KokoroTTSProvider",
    "ElevenLabsTTSProvider",
    "Wav2LipLipsyncProvider",
    "SyncLabsLipsyncProvider",
    "HeyGenVideoProvider",
    "DIDVideoProvider",
    "HiggsfieldVideoProvider",
    "ProviderManager",
]


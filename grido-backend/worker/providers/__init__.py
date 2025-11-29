"""
Providers module for TTS, lip-sync, and video generation.
"""

from .base import TTSProvider, LipsyncProvider, VideoProvider
from .kokoro_tts import KokoroTTSProvider
from .elevenlabs_tts import ElevenLabsTTSProvider
from .musetalk_lipsync import MuseTalkLipsyncProvider
from .heygen_video import HeyGenVideoProvider
from .manager import ProviderManager

__all__ = [
    "TTSProvider",
    "LipsyncProvider",
    "VideoProvider",
    "KokoroTTSProvider",
    "ElevenLabsTTSProvider",
    "MuseTalkLipsyncProvider",
    "HeyGenVideoProvider",
    "ProviderManager",
]


"""
ElevenLabs TTS Provider - API-based TTS.
"""

import os
import requests
from pathlib import Path
from typing import Optional

from .base import TTSProvider


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS provider using their API."""
    
    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        """
        Initialize ElevenLabs TTS provider.
        
        Args:
            api_key: ElevenLabs API key (defaults to ELEVENLABS_API_KEY env var)
            voice_id: Voice ID to use (defaults to PAPA_NOEL_VOICE_ID or "21m00Tcm4TlvDq8ikWAM")
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        # Usar voz de Papá Noel configurada, o fallback a default
        self.voice_id = voice_id or os.getenv("PAPA_NOEL_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.api_url = "https://api.elevenlabs.io/v1/text-to-speech"
    
    def is_available(self) -> bool:
        """Check if ElevenLabs is available (has API key)."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """
        Generate audio using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            
        Returns:
            Path to the generated audio file
        """
        if not self.is_available():
            raise Exception("ElevenLabs API key not configured")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure output is MP3 format (ElevenLabs default)
        if output_path.suffix not in [".mp3", ".wav"]:
            output_path = output_path.with_suffix(".mp3")
        
        url = f"{self.api_url}/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Multilingual model
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=120)
            response.raise_for_status()
            
            # Save audio file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Convert MP3 to WAV if needed (for compatibility with lip-sync)
            if output_path.suffix == ".mp3":
                wav_path = output_path.with_suffix(".wav")
                import subprocess
                subprocess.run(
                    [
                        "ffmpeg", "-i", str(output_path),
                        "-ar", "16000",  # 16kHz sample rate
                        "-ac", "1",  # Mono
                        "-y", str(wav_path)
                    ],
                    check=True,
                    capture_output=True
                )
                output_path.unlink()  # Remove MP3
                output_path = wav_path
            
            if not output_path.exists():
                raise Exception(f"ElevenLabs did not generate output file: {output_path}")
            
            return output_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"ElevenLabs API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"ElevenLabs TTS generation failed: {str(e)}")


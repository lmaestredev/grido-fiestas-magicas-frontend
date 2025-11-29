"""
Kokoro TTS Provider - Local GPU-based TTS.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from .base import TTSProvider


class KokoroTTSProvider(TTSProvider):
    """Kokoro TTS provider for local GPU-based text-to-speech."""
    
    def __init__(self, model_path: Optional[str] = None, speaker: str = "santa"):
        """
        Initialize Kokoro TTS provider.
        
        Args:
            model_path: Path to Kokoro model (optional, uses default if not provided)
            speaker: Speaker ID to use (default: "santa")
        """
        self.model_path = model_path or os.getenv("KOKORO_MODEL_PATH")
        self.speaker = speaker
        self.kokoro_script = os.getenv("KOKORO_SCRIPT_PATH", "kokoro/infer.py")
    
    def is_available(self) -> bool:
        """Check if Kokoro is available."""
        # Check if model path exists or if we can import kokoro
        if self.model_path and Path(self.model_path).exists():
            return True
        
        # Try to check if kokoro is installed
        try:
            result = subprocess.run(
                ["python", "-c", "import kokoro"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """
        Generate audio using Kokoro TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            
        Returns:
            Path to the generated audio file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure output is WAV format
        if output_path.suffix != ".wav":
            output_path = output_path.with_suffix(".wav")
        
        # Method 1: Using Kokoro CLI if available
        if Path(self.kokoro_script).exists():
            cmd = [
                "python",
                self.kokoro_script,
                "--text", text,
                "--output", str(output_path),
                "--speaker", self.speaker,
            ]
            
            if self.model_path:
                cmd.extend(["--model", self.model_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode != 0:
                raise Exception(f"Kokoro TTS failed: {result.stderr}")
        
        # Method 2: Using Kokoro Python API (if available)
        else:
            try:
                import kokoro
                
                # Generate audio using Kokoro API
                # Note: This is a placeholder - adjust based on actual Kokoro API
                audio_data = kokoro.generate(
                    text=text,
                    speaker=self.speaker,
                    model_path=self.model_path,
                )
                
                # Save audio to file
                import soundfile as sf
                sf.write(str(output_path), audio_data, 22050)  # Kokoro default sample rate
                
            except ImportError:
                raise Exception("Kokoro is not installed. Install with: pip install kokoro")
            except Exception as e:
                raise Exception(f"Kokoro TTS generation failed: {str(e)}")
        
        if not output_path.exists():
            raise Exception(f"Kokoro TTS did not generate output file: {output_path}")
        
        return output_path


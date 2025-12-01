"""
Wav2Lip Lip-sync Provider - Open-source lip-sync using Wav2Lip model.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .base import LipsyncProvider


class Wav2LipLipsyncProvider(LipsyncProvider):
    """Wav2Lip lip-sync provider for open-source lip synchronization."""
    
    def __init__(self, model_path: Optional[str] = None, repo_path: Optional[str] = None):
        """
        Initialize Wav2Lip lip-sync provider.
        
        Args:
            model_path: Path to Wav2Lip model file (wav2lip_gan.pth or wav2lip.pth)
            repo_path: Path to Wav2Lip repository root (optional)
        """
        self.model_path = model_path or os.getenv("WAV2LIP_MODEL_PATH")
        self.repo_path = Path(repo_path or os.getenv("WAV2LIP_REPO_PATH", "wav2lip"))
        self.script_path = self.repo_path / "inference.py"
    
    def is_available(self) -> bool:
        """Check if Wav2Lip is available."""
        # Check if model path exists
        if self.model_path and Path(self.model_path).exists():
            # Also check if script exists
            if self.script_path.exists():
                return True
        
        # Try to check if wav2lip is installed as package
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import wav2lip"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def apply_lipsync(self, video: Path, audio: Path, output_path: Path) -> Path:
        """
        Apply lip-sync using Wav2Lip.
        
        Args:
            video: Path to the base video (without audio)
            audio: Path to the audio file
            output_path: Path where the video with lip-sync should be saved
            
        Returns:
            Path to the generated video with lip-sync
        """
        if not video.exists():
            raise Exception(f"Input video not found: {video}")
        if not audio.exists():
            raise Exception(f"Input audio not found: {audio}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure output is MP4 format
        if output_path.suffix != ".mp4":
            output_path = output_path.with_suffix(".mp4")
        
        # Method 1: Using Wav2Lip repository script
        if self.script_path.exists() and self.model_path and Path(self.model_path).exists():
            # Change to repo directory
            original_cwd = Path.cwd()
            
            try:
                os.chdir(str(self.repo_path.absolute()))
                
                # Wav2Lip inference command
                # Usar ruta relativa al repositorio para el script
                script_rel_path = self.script_path.relative_to(self.repo_path) if self.repo_path in self.script_path.parents else self.script_path.name
                cmd = [
                    sys.executable,
                    str(script_rel_path),
                    "--checkpoint_path", str(Path(self.model_path).absolute()),
                    "--face", str(video.absolute()),
                    "--audio", str(audio.absolute()),
                    "--outfile", str(output_path.absolute()),
                ]
                
                # Optional: Add face detection model if available
                face_det_model = os.getenv("WAV2LIP_FACE_DET_MODEL")
                if face_det_model and Path(face_det_model).exists():
                    cmd.extend(["--face_det_batch_size", "1"])
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes max
                )
                
                if result.returncode != 0:
                    raise Exception(f"Wav2Lip lip-sync failed: {result.stderr}")
                
            finally:
                os.chdir(original_cwd)
        
        # Method 2: Using Wav2Lip as installed package
        else:
            try:
                # Try to use Wav2Lip as a Python package
                import wav2lip
                
                # If wav2lip has a simple API
                if hasattr(wav2lip, 'inference'):
                    wav2lip.inference(
                        checkpoint_path=self.model_path,
                        face_path=str(video),
                        audio_path=str(audio),
                        output_path=str(output_path),
                    )
                else:
                    # Fallback: use subprocess with wav2lip command
                    cmd = [
                        "wav2lip",
                        "--checkpoint", self.model_path or "wav2lip_gan.pth",
                        "--face", str(video),
                        "--audio", str(audio),
                        "--outfile", str(output_path),
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"Wav2Lip lip-sync failed: {result.stderr}")
            
            except ImportError:
                raise Exception(
                    "Wav2Lip is not installed. "
                    "Install with: git clone https://github.com/Rudrabha/Wav2Lip.git && "
                    "cd Wav2Lip && pip install -r requirements.txt"
                )
            except Exception as e:
                raise Exception(f"Wav2Lip lip-sync failed: {str(e)}")
        
        if not output_path.exists():
            raise Exception(f"Wav2Lip did not generate output file: {output_path}")
        
        return output_path


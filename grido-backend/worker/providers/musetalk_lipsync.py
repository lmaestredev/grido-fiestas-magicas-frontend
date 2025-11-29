"""
MuseTalk Lip-sync Provider - Local GPU-based lip-sync.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

from .base import LipsyncProvider


class MuseTalkLipsyncProvider(LipsyncProvider):
    """MuseTalk lip-sync provider for local GPU-based lip synchronization."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize MuseTalk lip-sync provider.
        
        Args:
            model_path: Path to MuseTalk model (optional, uses default if not provided)
        """
        self.model_path = model_path or os.getenv("MUSETALK_MODEL_PATH")
        self.musetalk_script = os.getenv("MUSETALK_SCRIPT_PATH", "musetalk/realtime_inference.py")
    
    def is_available(self) -> bool:
        """Check if MuseTalk is available."""
        # Check if model path exists
        if self.model_path and Path(self.model_path).exists():
            return True
        
        # Try to check if musetalk is installed
        try:
            result = subprocess.run(
                ["python", "-c", "import musetalk"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def apply_lipsync(self, video: Path, audio: Path, output_path: Path) -> Path:
        """
        Apply lip-sync using MuseTalk.
        
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
        
        # Method 1: Using MuseTalk CLI if available
        if Path(self.musetalk_script).exists():
            result_dir = output_path.parent
            
            cmd = [
                "python", "-m", "musetalk.realtime_inference",
                "--inference_config", "configs/inference/realtime.yaml",
                "--video_path", str(video),
                "--audio_path", str(audio),
                "--result_dir", str(result_dir),
                "--preparation", "False",
                "--version", "v15",
                "--fps", "25",
            ]
            
            if self.model_path:
                cmd.extend(["--model_path", self.model_path])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            if result.returncode != 0:
                raise Exception(f"MuseTalk lip-sync failed: {result.stderr}")
            
            # MuseTalk typically outputs to a subdirectory, find the output file
            output_files = list(result_dir.glob("**/*.mp4"))
            if output_files:
                # Use the most recent output file
                output_file = max(output_files, key=lambda p: p.stat().st_mtime)
                if output_file != output_path:
                    # Copy to desired location
                    import shutil
                    shutil.copy2(output_file, output_path)
        
        # Method 2: Using MuseTalk Python API (if available)
        else:
            try:
                from musetalk import MuseTalk
                
                # Initialize MuseTalk
                musetalk = MuseTalk(model_path=self.model_path)
                
                # Apply lip-sync
                musetalk.process(
                    video_path=str(video),
                    audio_path=str(audio),
                    output_path=str(output_path),
                )
                
            except ImportError:
                raise Exception("MuseTalk is not installed. Install with: pip install musetalk")
            except Exception as e:
                raise Exception(f"MuseTalk lip-sync failed: {str(e)}")
        
        if not output_path.exists():
            raise Exception(f"MuseTalk did not generate output file: {output_path}")
        
        return output_path


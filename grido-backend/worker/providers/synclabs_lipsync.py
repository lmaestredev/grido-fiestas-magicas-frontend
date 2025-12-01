"""
Sync Labs Lip-sync Provider - Commercial HD lip-sync API.

Sync Labs es la versión comercial y mejorada de Wav2Lip, con modelos HD
y soporte comercial. Requiere API key.
"""

import os
import requests
import time
from pathlib import Path
from typing import Optional

from .base import LipsyncProvider


class SyncLabsLipsyncProvider(LipsyncProvider):
    """Sync Labs lip-sync provider using their commercial API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Sync Labs lip-sync provider.
        
        Args:
            api_key: Sync Labs API key (defaults to SYNCLABS_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("SYNCLABS_API_KEY")
        # Sync Labs API - verificar documentación actualizada para el endpoint correcto
        # Puede ser: https://api.synclabs.so o https://synclabs.so/api
        self.api_base_url = os.getenv("SYNCLABS_API_BASE_URL", "https://api.synclabs.so")
        self.poll_interval = 5  # seconds
        self.max_poll_time = 600  # 10 minutes max
    
    def is_available(self) -> bool:
        """Check if Sync Labs is available (has API key)."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def apply_lipsync(self, video: Path, audio: Path, output_path: Path) -> Path:
        """
        Apply lip-sync using Sync Labs API.
        
        Args:
            video: Path to the base video (without audio)
            audio: Path to the audio file
            output_path: Path where the video with lip-sync should be saved
            
        Returns:
            Path to the generated video with lip-sync
        """
        if not self.is_available():
            raise Exception("Sync Labs API key not configured")
        
        if not video.exists():
            raise Exception(f"Input video not found: {video}")
        if not audio.exists():
            raise Exception(f"Input audio not found: {audio}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Upload video and audio
        video_url = self._upload_file(video)
        audio_url = self._upload_file(audio)
        
        # Step 2: Create lip-sync job
        job_id = self._create_job(video_url, audio_url)
        
        # Step 3: Poll for completion
        result_url = self._poll_job(job_id)
        
        # Step 4: Download result
        return self._download_result(result_url, output_path)
    
    def _upload_file(self, file_path: Path) -> str:
        """Upload file to Sync Labs and return URL."""
        url = f"{self.api_base_url}/v1/upload"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            response = requests.post(url, headers=headers, files=files, timeout=300)
            response.raise_for_status()
            result = response.json()
            return result.get("url") or result.get("file_url")
    
    def _create_job(self, video_url: str, audio_url: str) -> str:
        """Create lip-sync job and return job ID."""
        url = f"{self.api_base_url}/v1/lipsync"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        data = {
            "video_url": video_url,
            "audio_url": audio_url,
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("job_id") or result.get("id")
    
    def _poll_job(self, job_id: str) -> str:
        """Poll job status and return result URL when complete."""
        url = f"{self.api_base_url}/v1/lipsync/{job_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        start_time = time.time()
        while time.time() - start_time < self.max_poll_time:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            status = result.get("status")
            if status == "completed":
                return result.get("result_url") or result.get("video_url")
            elif status == "failed":
                error = result.get("error", "Unknown error")
                raise Exception(f"Sync Labs job failed: {error}")
            
            time.sleep(self.poll_interval)
        
        raise Exception(f"Sync Labs job timed out after {self.max_poll_time} seconds")
    
    def _download_result(self, result_url: str, output_path: Path) -> Path:
        """Download result video from URL."""
        response = requests.get(result_url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path


"""
HeyGen Video Provider - API-based complete video generation (TTS + lip-sync).
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from .base import VideoProvider


class HeyGenVideoProvider(VideoProvider):
    """HeyGen video provider using their API for complete video generation."""
    
    def __init__(self, api_key: Optional[str] = None, avatar_id: Optional[str] = None):
        """
        Initialize HeyGen video provider.
        
        Args:
            api_key: HeyGen API key (defaults to HEYGEN_API_KEY env var)
            avatar_id: Avatar ID to use (defaults to PAPA_NOEL_AVATAR_ID or "default")
        """
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        # Usar avatar de Papá Noel configurado, o fallback a default
        self.avatar_id = avatar_id or os.getenv("PAPA_NOEL_AVATAR_ID", "default")
        # HeyGen API v2 endpoint (más reciente)
        self.api_base_url = os.getenv("HEYGEN_API_BASE_URL", "https://api.heygen.com/v2")
        self.poll_interval = 5  # seconds
        self.max_poll_time = 600  # 10 minutes max
    
    def is_available(self) -> bool:
        """Check if HeyGen is available (has API key)."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _poll_video_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll HeyGen API for video generation status.
        
        Args:
            task_id: Task ID returned by HeyGen API
            
        Returns:
            Status response from API
        """
        url = f"{self.api_base_url}/video_status.get"
        
        headers = {
            "X-API-KEY": self.api_key,  # Según documentación: https://docs.heygen.com/docs/quick-start
            "Content-Type": "application/json",
        }
        
        data = {
            "task_id": task_id,
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def _download_video(self, video_url: str, output_path: Path) -> Path:
        """
        Download video from HeyGen URL.
        
        Args:
            video_url: URL of the generated video
            output_path: Path where the video should be saved
            
        Returns:
            Path to the downloaded video
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(video_url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def generate_video(self, script: str, avatar_id: str, output_path: Path, **kwargs) -> Path:
        """
        Generate a complete video with TTS and lip-sync using HeyGen API.
        
        Args:
            script: Text script for the video
            avatar_id: ID of the avatar/character to use
            output_path: Path where the video should be saved
            **kwargs: Additional parameters (voice_id, etc.)
            
        Returns:
            Path to the generated video
        """
        if not self.is_available():
            raise Exception("HeyGen API key not configured")
        
        # Use provided avatar_id or default
        avatar = avatar_id or self.avatar_id
        
        # Step 1: Create video generation task
        # Según documentación: https://docs.heygen.com/docs/quick-start
        # El endpoint correcto para "Create Avatar Videos (V2)" es:
        # POST https://api.heygen.com/v2/avatar/video
        # O alternativamente: POST https://api.heygen.com/v1/video/talking_photo
        endpoints_to_try = [
            f"{self.api_base_url}/avatar/video",  # Endpoint v2 más probable
            f"{self.api_base_url}/video/talking_photo",  # v2 talking photo
            "https://api.heygen.com/v1/video/talking_photo",  # v1 fallback
            "https://api.heygen.com/v1/talking_photo",  # alternativa v1
        ]
        
        headers = {
            "X-API-KEY": self.api_key,  # Según documentación: https://docs.heygen.com/docs/quick-start
            "Content-Type": "application/json",
        }
        
        # Estructura de datos según documentación de HeyGen
        # Intentar con diferentes estructuras según la versión de la API
        data_variants = [
            # Estructura v2 (más probable)
            {
                "video_input_config": {
                    "avatar_id": avatar,
                    "text": script,
                },
                "voice": {
                    "voice_id": kwargs.get("voice_id") or os.getenv("PAPA_NOEL_VOICE_ID", "default"),
                },
                "caption": kwargs.get("caption", False),
                "dimension": {
                    "width": 1080,
                    "height": 1920,
                },
            },
            # Estructura v1 (fallback)
            {
                "avatar_id": avatar,
                "text": script,
                "voice_id": kwargs.get("voice_id") or os.getenv("PAPA_NOEL_VOICE_ID", "default"),
                "caption": kwargs.get("caption", False),
            },
            # Estructura simplificada
            {
                "avatar_id": avatar,
                "text": script,
            },
        ]
        
        # Add any additional parameters from kwargs
        if "background" in kwargs:
            data["background"] = kwargs["background"]
        if "subtitle" in kwargs:
            data["subtitle"] = kwargs["subtitle"]
        
        try:
            # Intentar diferentes endpoints y estructuras
            last_error = None
            task_id = None
            
            for url in endpoints_to_try:
                for data_variant in data_variants:
                    try:
                        response = requests.post(url, json=data_variant, headers=headers, timeout=30)
                        if response.status_code == 200 or response.status_code == 201:
                            result = response.json()
                            task_id = result.get("data", {}).get("task_id") or result.get("task_id")
                            
                            if task_id:
                                break  # Éxito, salir de los loops
                            else:
                                last_error = f"HeyGen API did not return task_id: {result}"
                        else:
                            last_error = f"HeyGen API returned {response.status_code}: {response.text}"
                    except requests.exceptions.RequestException as e:
                        last_error = f"HeyGen API request failed for {url}: {str(e)}"
                        continue
                
                if task_id:
                    break
            
            if not task_id:
                raise Exception(f"HeyGen API failed on all endpoints. Last error: {last_error}")
            
            # Step 2: Poll for video completion
            start_time = time.time()
            while time.time() - start_time < self.max_poll_time:
                status_response = self._poll_video_status(task_id)
                
                status_data = status_response.get("data", {})
                status = status_data.get("status")
                
                if status == "completed":
                    video_url = status_data.get("video_url")
                    if not video_url:
                        raise Exception("HeyGen video completed but no URL provided")
                    
                    # Step 3: Download video
                    return self._download_video(video_url, output_path)
                
                elif status == "failed":
                    error_msg = status_data.get("error", "Unknown error")
                    raise Exception(f"HeyGen video generation failed: {error_msg}")
                
                # Status is "processing" or "pending", wait and retry
                time.sleep(self.poll_interval)
            
            raise Exception(f"HeyGen video generation timed out after {self.max_poll_time} seconds")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HeyGen API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"HeyGen video generation failed: {str(e)}")


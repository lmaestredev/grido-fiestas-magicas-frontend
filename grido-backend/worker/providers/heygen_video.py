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
    
    def __init__(self, api_key: Optional[str] = None, avatar_id: str = "default"):
        """
        Initialize HeyGen video provider.
        
        Args:
            api_key: HeyGen API key (defaults to HEYGEN_API_KEY env var)
            avatar_id: Avatar ID to use (default: "default")
        """
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")
        self.avatar_id = avatar_id
        self.api_base_url = "https://api.heygen.com/v1"
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
            "X-Api-Key": self.api_key,
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
        url = f"{self.api_base_url}/video.generate"
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        
        data = {
            "video_input_config": {
                "avatar_id": avatar,
                "text": script,
            },
            "voice": {
                "voice_id": kwargs.get("voice_id", "default"),
            },
            "caption": kwargs.get("caption", False),
            "dimension": {
                "width": 1080,
                "height": 1920,
            },
        }
        
        # Add any additional parameters from kwargs
        if "background" in kwargs:
            data["background"] = kwargs["background"]
        if "subtitle" in kwargs:
            data["subtitle"] = kwargs["subtitle"]
        
        try:
            # Submit video generation request
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get("data", {}).get("task_id")
            
            if not task_id:
                raise Exception(f"HeyGen API did not return task_id: {result}")
            
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


"""
Higgsfield Video Provider - API-based video generation.
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from .base import VideoProvider


class HiggsfieldVideoProvider(VideoProvider):
    """Higgsfield video provider using their API for video generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Higgsfield video provider.
        
        Args:
            api_key: Higgsfield API key (defaults to HIGGSFIELD_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("HIGGSFIELD_API_KEY")
        self.api_key_id = os.getenv("HIGGSFIELD_API_KEY_ID")
        self.api_key_secret = os.getenv("HIGGSFIELD_API_KEY_SECRET")
        self.api_base_url = os.getenv("HIGGSFIELD_API_BASE_URL", "https://cloud.higgsfield.ai/api")
        self.poll_interval = 5  # seconds
        self.max_poll_time = 600  # 10 minutes max
    
    def is_available(self) -> bool:
        """Check if Higgsfield is available (has API key)."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _poll_video_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll Higgsfield API for video generation status.
        
        Args:
            task_id: Task ID returned by Higgsfield API
            
        Returns:
            Status response from API
        """
        # Probar diferentes endpoints de status
        status_endpoints = [
            f"{self.api_base_url}/status/{task_id}",
            f"{self.api_base_url}/v1/status/{task_id}",
            f"{self.api_base_url}/generation/{task_id}",
            f"{self.api_base_url}/v1/generation/{task_id}",
        ]
        
        # Probar diferentes métodos de autenticación
        headers_variants = [
            {
                "Authorization": f"Bearer {self.api_key_id}",
                "X-API-Key": self.api_key_secret,
            },
            {
                "Authorization": f"Bearer {self.api_key_secret}",
                "X-API-Key": self.api_key_id,
            },
            {
                "X-API-Key-ID": self.api_key_id,
                "X-API-Key-Secret": self.api_key_secret,
            },
        ]
        
        for url in status_endpoints:
            for headers in headers_variants:
                try:
                    response = requests.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        return response.json()
                except:
                    continue
        
        raise Exception(f"Could not poll status for task {task_id}")
    
    def _download_video(self, video_url: str, output_path: Path) -> Path:
        """
        Download video from Higgsfield URL.
        
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
        Generate a video using Higgsfield API.
        
        Args:
            script: Text script for the video
            avatar_id: ID of the avatar/character to use (may not be applicable)
            output_path: Path where the video should be saved
            **kwargs: Additional parameters
            
        Returns:
            Path to the generated video
        """
        if not self.is_available():
            raise Exception("Higgsfield API key not configured")
        
        # Higgsfield API endpoints to try
        endpoints_to_try = [
            f"{self.api_base_url}/generate",
            f"{self.api_base_url}/v1/generate",
            f"{self.api_base_url}/video/generate",
        ]
        
        # Headers variants to try
        headers_variants = []
        if self.api_key:
            headers_variants.append({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })
        if self.api_key_id and self.api_key_secret:
            headers_variants.extend([
                {
                    "Authorization": f"Bearer {self.api_key_id}",
                    "X-API-Key": self.api_key_secret,
                    "Content-Type": "application/json",
                },
                {
                    "Authorization": f"Bearer {self.api_key_secret}",
                    "X-API-Key": self.api_key_id,
                    "Content-Type": "application/json",
                },
                {
                    "X-API-Key-ID": self.api_key_id,
                    "X-API-Key-Secret": self.api_key_secret,
                    "Content-Type": "application/json",
                },
            ])
        
        if not headers_variants:
            raise Exception("No Higgsfield API credentials configured")
        
        # Data structures to try
        data_variants = [
            # Variant 1: Standard structure
            {
                "prompt": script,
                "duration": kwargs.get("duration", 10),
                "resolution": kwargs.get("resolution", {"width": 1080, "height": 1920}),
                "style": kwargs.get("style", "realistic"),
            },
            # Variant 2: Simplified
            {
                "text": script,
                "duration": kwargs.get("duration", 10),
            },
            # Variant 3: With avatar
            {
                "prompt": script,
                "avatar_id": avatar_id,
                "duration": kwargs.get("duration", 10),
            },
        ]
        
        try:
            last_error = None
            task_id = None
            
            for url in endpoints_to_try:
                for headers in headers_variants:
                    for data_variant in data_variants:
                        try:
                            response = requests.post(url, json=data_variant, headers=headers, timeout=30)
                            if response.status_code == 200 or response.status_code == 201:
                                result = response.json()
                                task_id = result.get("task_id") or result.get("id") or result.get("generation_id")
                                
                                if task_id:
                                    break
                                else:
                                    last_error = f"Higgsfield API did not return task_id: {result}"
                            else:
                                last_error = f"Higgsfield API returned {response.status_code}: {response.text}"
                        except requests.exceptions.RequestException as e:
                            last_error = f"Higgsfield API request failed for {url}: {str(e)}"
                            continue
                    
                    if task_id:
                        break
                
                if task_id:
                    break
            
            if not task_id:
                raise Exception(f"Higgsfield API failed on all endpoints. Last error: {last_error}")
            
            # Poll for video completion
            start_time = time.time()
            while time.time() - start_time < self.max_poll_time:
                status_response = self._poll_video_status(task_id)
                
                status = status_response.get("status") or status_response.get("state")
                
                if status == "completed" or status == "done":
                    video_url = status_response.get("video_url") or status_response.get("url") or status_response.get("result_url")
                    if not video_url:
                        raise Exception("Higgsfield video completed but no URL provided")
                    
                    return self._download_video(video_url, output_path)
                
                elif status == "failed" or status == "error":
                    error_msg = status_response.get("error", "Unknown error")
                    raise Exception(f"Higgsfield video generation failed: {error_msg}")
                
                # Status is "processing" or "pending", wait and retry
                time.sleep(self.poll_interval)
            
            raise Exception(f"Higgsfield video generation timed out after {self.max_poll_time} seconds")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Higgsfield API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Higgsfield video generation failed: {str(e)}")


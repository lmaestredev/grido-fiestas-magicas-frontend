"""
HeyGen Video Provider - API-based complete video generation (TTS + lip-sync).
"""

import os
import time
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from .base import VideoProvider

logger = logging.getLogger(__name__)


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
    
    def _get_avatar_voice_id(self, avatar_id: str) -> Optional[str]:
        """
        Obtiene el voice_id asociado a un avatar desde HeyGen API.
        
        Args:
            avatar_id: ID del avatar
            
        Returns:
            voice_id del avatar si está disponible, None en caso contrario
        """
        try:
            url = f"https://api.heygen.com/v2/avatars/{avatar_id}"
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json",
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # El voice_id puede estar en diferentes lugares según la respuesta
                voice_id = (
                    data.get("data", {}).get("voice_id") or
                    data.get("data", {}).get("default_voice_id") or
                    data.get("voice_id") or
                    data.get("default_voice_id")
                )
                if voice_id:
                    logger.info(f"[HeyGen] Voice ID del avatar {avatar_id}: {voice_id}")
                    return voice_id
        except Exception as e:
            logger.debug(f"[HeyGen] No se pudo obtener voice_id del avatar: {str(e)}")
        return None
    
    def _poll_video_status(self, task_id: str) -> Dict[str, Any]:
        """
        Poll HeyGen API for video generation status.
        
        Args:
            task_id: Task/Video ID returned by HeyGen API
            
        Returns:
            Status response from API
        """
        # Endpoints posibles según distintas versiones de la API / documentación
        # Referencia: https://docs.heygen.com/docs/create-video (Retrieve Video Status/Details)
        endpoints = [
            f"https://api.heygen.com/v2/video/{task_id}",              # v2 (documentación reciente)
            f"https://api.heygen.com/v1/video/{task_id}",              # v1 (compatibilidad)
            f"https://api.heygen.com/v2/video/status?video_id={task_id}",  # v2 con query param
            f"https://api.heygen.com/v1/video/status?video_id={task_id}",  # v1 con query param
        ]
        
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }
        
        last_error = None
        for url in endpoints:
            try:
                logger.info(f"[HeyGen] Consultando estado de video en: {url}")
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response.json()
                else:
                    last_error = f"Status {response.status_code}: {response.text[:300]}"
                    logger.warning(f"[HeyGen] ⚠️ Status endpoint fallo: {last_error}")
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(f"[HeyGen] ⚠️ Error consultando estado: {last_error}")
                continue
        
        raise Exception(f"Failed to get video status: {last_error or 'All status endpoints failed'}")
    
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
        
        # Use provided avatar_id or default (en nuestro caso, talking_photo_id)
        avatar = avatar_id or self.avatar_id
        
        # Validar que el ID sea válido (debe ser un string largo, no "default" o números cortos)
        if avatar == "default" or (isinstance(avatar, str) and len(avatar) < 10):
            error_msg = (
                f"Avatar/Talking photo ID '{avatar}' no es válido. Necesitas un ID real de tu cuenta de HeyGen.\n"
                "💡 Los IDs válidos son strings largos (ejemplo: 4e96c6c0514e4f5cbbed14f8e8624084)\n"
                "   Para obtener IDs válidos:\n"
                "   1. Ve a https://app.heygen.com\n"
                "   2. Selecciona un avatar o talking photo\n"
                "   3. Copia su ID completo\n"
                "   4. Configúralo en .env: PAPA_NOEL_AVATAR_ID=tu_avatar_id_real"
            )
            logger.error(f"[HeyGen] ❌ {error_msg}")
            raise Exception(error_msg)
        
        # Step 1: Create video generation task
        # Según documentación oficial de HeyGen API v2 (Developer Guide):
        # https://docs.heygen.com/docs/create-video
        # Endpoint: POST https://api.heygen.com/v2/video/generate
        url = "https://api.heygen.com/v2/video/generate"
        
        headers = {
            "X-Api-Key": self.api_key,  # Autenticación: https://docs.heygen.com/reference/authentication
            "Content-Type": "application/json",
        }
        
        # Obtener voice_id
        # Prioridad: parámetro > voice_id del avatar > PAPA_NOEL_VOICE_ID_HEYGEN > PAPA_NOEL_VOICE_ID
        voice_id = kwargs.get("voice_id")
        
        if not voice_id:
            logger.info(f"[HeyGen] Intentando obtener voice_id del avatar {avatar}...")
            voice_id = self._get_avatar_voice_id(avatar)
        
        if not voice_id:
            voice_id = (
                os.getenv("PAPA_NOEL_VOICE_ID_HEYGEN") or
                os.getenv("PAPA_NOEL_VOICE_ID")
            )
        
        if not voice_id:
            raise Exception(
                "voice_id es requerido para HeyGen API. "
                "Configura PAPA_NOEL_VOICE_ID_HEYGEN en .env o pasa voice_id como parámetro."
            )
        
        logger.info(f"[HeyGen] Usando voice_id: {voice_id}")
        
        # Payload alineado con la guía oficial "Create Avatar Videos (V2)"
        # Referencia (Developer Guide): https://docs.heygen.com/docs/create-video
        # Estructura base:
        # {
        #   "video_inputs": [
        #     {
        #       "character": { "type": "avatar", "avatar_id": "...", "avatar_style": "normal" },
        #       "voice": {
        #         "type": "text",
        #         "input_text": "Hello...",
        #         "voice_id": "...",
        #         "speed": 1.0
        #       }
        #     }
        #   ],
        #   "dimension": { "width": 1080, "height": 1920 }
        # }
        video_title = kwargs.get("video_title") or "Mensaje de Papá Noel"
        dimension = kwargs.get("dimension") or {"width": 1080, "height": 1920}
        voice_speed = float(kwargs.get("voice_speed", 1.0))

        # Permitir elegir tipo de character por kwargs/env (default: talking_photo)
        # Para Papá Noel usamos talking_photo_id (PHOTO avatar)
        character_type = (
            kwargs.get("character_type")
            or os.getenv("HEYGEN_CHARACTER_TYPE")
            or "talking_photo"
        )

        if character_type == "talking_photo":
            character_obj = {
                "type": "talking_photo",
                "talking_photo_id": avatar,
                "scale": float(kwargs.get("tp_scale", 0.93)),
                "talking_photo_style": kwargs.get("tp_style", "square"),
                "offset": kwargs.get("tp_offset", {"x": 0, "y": 0}),
                "talking_style": kwargs.get("tp_talking_style", "expressive"),
                "expression": kwargs.get("tp_expression", "happy"),
                "super_resolution": bool(kwargs.get("tp_super_resolution", True)),
                "matting": bool(kwargs.get("tp_matting", False)),
                "circle_background_color": kwargs.get("tp_circle_bg", "#FFFFFF"),
            }
        else:
            # Fallback: avatar clásico
            character_obj = {
                "type": "avatar",
                "avatar_id": avatar,
                "avatar_style": "normal",
            }
        
        voice_obj = {
            "type": "text",
            "input_text": script,
            "voice_id": voice_id,
            "speed": voice_speed,
        }
        
        payload: Dict[str, Any] = {
            "video_title": video_title,
            "video_inputs": [
                {
                    "character": character_obj,
                    "voice": voice_obj,
                }
            ],
            "dimension": dimension,
        }
        
        try:
            logger.info(f"[HeyGen] Enviando solicitud a {url}")
            logger.debug(f"[HeyGen] Payload: {payload}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            logger.debug(f"[HeyGen] Response status: {response.status_code}")
            logger.debug(f"[HeyGen] Response body: {response.text[:500]}")
            
            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                except Exception:
                    error_data = response.text[:500]
                raise Exception(f"HeyGen create video failed: {error_data}")
            
            result = response.json()
            logger.info(f"[HeyGen] ✅ Video creation request accepted")
            
            # video_id puede venir como top-level o dentro de data
            task_id = (
                result.get("data", {}).get("video_id") or
                result.get("data", {}).get("id") or
                result.get("video_id") or
                result.get("id")
            )
            
            if not task_id:
                raise Exception(f"HeyGen API did not return video_id: {result}")
            
            # Step 2: Poll for video completion
            start_time = time.time()
            while time.time() - start_time < self.max_poll_time:
                status_response = self._poll_video_status(task_id)
                
                # El MCP retorna status directamente o dentro de data
                status_data = status_response.get("data", {}) or status_response
                status = status_data.get("status") or status_response.get("status")
                
                if status == "completed" or status == "success":
                    # El MCP retorna video_url directamente o dentro de data
                    video_url = (
                        status_data.get("video_url") or 
                        status_response.get("video_url") or
                        status_data.get("url")
                    )
                    if not video_url:
                        raise Exception("HeyGen video completed but no URL provided")
                    
                    # Step 3: Download video
                    return self._download_video(video_url, output_path)
                
                elif status == "failed" or status == "error":
                    error_msg = (
                        status_data.get("error", {}).get("message") or
                        status_data.get("error") or
                        status_response.get("error", {}).get("message") or
                        "Unknown error"
                    )
                    raise Exception(f"HeyGen video generation failed: {error_msg}")
                
                # Status is "processing" or "pending", wait and retry
                time.sleep(self.poll_interval)
            
            raise Exception(f"HeyGen video generation timed out after {self.max_poll_time} seconds")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HeyGen API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"HeyGen video generation failed: {str(e)}")


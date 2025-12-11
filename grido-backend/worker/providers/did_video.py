"""
D-ID Video Provider - API-based complete video generation (TTS + lip-sync).
"""

import os
import time
import logging
import requests
import base64
from pathlib import Path
from typing import Optional, Dict, Any

from .base import VideoProvider

logger = logging.getLogger(__name__)


class DIDVideoProvider(VideoProvider):
    """
    D-ID video provider using their API for complete video generation.
    
    ⚠️ IMPORTANTE: D-ID requiere fotos reales de personas.
    No funciona con ilustraciones, dibujos, diseños o personajes animados.
    Si necesitas usar un avatar ilustrado, considera HeyGen o Higgsfield.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize D-ID video provider.
        
        Args:
            api_key: D-ID API key (defaults to DID_API_KEY or DID_API_KEY_PLAIN env var)
        """
        # D-ID usa Basic Authentication con Base64
        api_key_encoded = os.getenv("DID_API_KEY")
        api_key_plain = os.getenv("DID_API_KEY_PLAIN")
        
        if api_key:
            # Si se pasa directamente, asumir que ya está codificado
            self.api_key = api_key
        elif api_key_encoded:
            # Si está en env como DID_API_KEY, asumir que ya está codificado
            self.api_key = api_key_encoded
        elif api_key_plain:
            # Si está como DID_API_KEY_PLAIN, codificar a Base64
            # D-ID usa formato: base64(api_key:)
            api_key_with_colon = f"{api_key_plain}:"
            self.api_key = base64.b64encode(api_key_with_colon.encode()).decode()
        else:
            self.api_key = None
        
        self.api_base_url = os.getenv("DID_API_BASE_URL", "https://api.d-id.com")
        self.poll_interval = 5  # seconds
        self.max_poll_time = 600  # 10 minutes max
    
    def is_available(self) -> bool:
        """Check if D-ID is available (has API key)."""
        return self.api_key is not None and len(self.api_key) > 0
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for D-ID API."""
        return {
            "accept": "application/json",
            "authorization": f"Basic {self.api_key}",
        }
    
    def _upload_image(self, image_path: Path) -> str:
        """
        Upload image to D-ID and return source_url.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            source_url from D-ID API
        """
        if not image_path.exists():
            raise Exception(f"Image file not found: {image_path}")
        
        url = f"{self.api_base_url}/images"
        headers = {
            **self._get_auth_headers(),
            "content-type": "multipart/form-data",
        }
        
        try:
            with open(image_path, "rb") as f:
                files = {"image": (image_path.name, f, "image/png")}
                # requests maneja multipart/form-data automáticamente, no incluir content-type
                headers_without_content_type = self._get_auth_headers()
                response = requests.post(url, files=files, headers=headers_without_content_type, timeout=30)
            
            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                except Exception:
                    error_data = response.text[:500]
                raise Exception(f"D-ID upload image failed: {error_data}")
            
            result = response.json()
            # D-ID retorna {"url": "...", "id": "..."}
            source_url = result.get("url") or result.get("source_url")
            if not source_url:
                raise Exception(f"D-ID did not return image URL: {result}")
            
            logger.info(f"[D-ID] ✅ Imagen subida: {source_url}")
            return source_url
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"D-ID upload image request failed: {str(e)}")
    
    def _upload_audio(self, audio_path: Path) -> str:
        """
        Upload audio to D-ID and return audio_url.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            audio_url from D-ID API
        """
        if not audio_path.exists():
            raise Exception(f"Audio file not found: {audio_path}")
        
        url = f"{self.api_base_url}/audios"
        headers = self._get_auth_headers()
        
        try:
            # Determinar content type según extensión
            ext = audio_path.suffix.lower()
            content_type_map = {
                ".mp3": "audio/mpeg",
                ".wav": "audio/wav",
                ".m4a": "audio/m4a",
                ".ogg": "audio/ogg",
            }
            content_type = content_type_map.get(ext, "audio/mpeg")
            
            with open(audio_path, "rb") as f:
                files = {"audio": (audio_path.name, f, content_type)}
                response = requests.post(url, files=files, headers=headers, timeout=30)
            
            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                except Exception:
                    error_data = response.text[:500]
                raise Exception(f"D-ID upload audio failed: {error_data}")
            
            result = response.json()
            # D-ID retorna {"url": "...", "id": "..."}
            audio_url = result.get("url") or result.get("audio_url")
            if not audio_url:
                raise Exception(f"D-ID did not return audio URL: {result}")
            
            logger.info(f"[D-ID] ✅ Audio subido: {audio_url}")
            return audio_url
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"D-ID upload audio request failed: {str(e)}")
    
    def _create_talk(self, source_url: str, audio_url: str) -> str:
        """
        Create a talk in D-ID with image and audio.
        
        Args:
            source_url: URL of the uploaded image
            audio_url: URL of the uploaded audio
            
        Returns:
            talk_id from D-ID API
        """
        url = f"{self.api_base_url}/talks"
        headers = {
            **self._get_auth_headers(),
            "content-type": "application/json",
        }
        
        payload = {
            "source_url": source_url,
            "script": {
                "type": "audio",
                "audio_url": audio_url,
            }
        }
        
        try:
            logger.info(f"[D-ID] Creando talk con source_url: {source_url[:50]}...")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                    # Detectar error de "face not detected" y dar mensaje más claro
                    error_kind = error_data.get("error", {}).get("kind") if isinstance(error_data.get("error"), dict) else None
                    error_description = error_data.get("error", {}).get("description") if isinstance(error_data.get("error"), dict) else None
                    
                    if error_kind == "FaceError" or (error_description and "face not detected" in str(error_description).lower()):
                        raise Exception(
                            "D-ID no pudo detectar una cara humana en la imagen. "
                            "D-ID requiere fotos reales de personas, no funciona con ilustraciones, dibujos o diseños. "
                            "Si estás usando una imagen de Papá Noel ilustrado, considera usar HeyGen o Higgsfield que soportan avatares personalizados."
                        )
                except Exception as e:
                    if "D-ID no pudo detectar" in str(e):
                        raise

                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:500]
                    raise Exception(f"D-ID create talk failed: {error_data}")
            
            result = response.json()
            # D-ID retorna {"id": "talk_id", "status": "created", ...}
            talk_id = result.get("id") or result.get("talk_id")
            if not talk_id:
                raise Exception(f"D-ID did not return talk ID: {result}")
            
            logger.info(f"[D-ID] ✅ Talk creado: {talk_id}")
            return talk_id
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"D-ID create talk request failed: {str(e)}")
    
    def _poll_talk_status(self, talk_id: str) -> Dict[str, Any]:
        """
        Poll D-ID API for talk status.
        
        Args:
            talk_id: Talk ID returned by D-ID API
            
        Returns:
            Status response from API
        """
        url = f"{self.api_base_url}/talks/{talk_id}"
        headers = self._get_auth_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Status {response.status_code}: {response.text[:300]}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"D-ID poll status request failed: {str(e)}")
    
    def _download_video(self, video_url: str, output_path: Path) -> Path:
        """
        Download video from D-ID URL.
        
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
        Generate a complete video with TTS and lip-sync using D-ID API.
        
        D-ID requiere:
        1. Audio pre-generado (no acepta texto directamente)
        2. Imagen subida a D-ID
        3. Crear talk con imagen y audio
        
        Args:
            script: Text script for the video (se ignora, se usa audio_path)
            avatar_id: ID de avatar (se ignora, se usa image_path)
            output_path: Path where the video should be saved
            **kwargs: Additional parameters:
                - audio_path: Path to pre-generated audio file (REQUIRED)
                - image_path: Path to image file (defaults to PAPA_NOEL_IMAGE_PATH or assets/Grido_PapaNoel.png)
                
        Returns:
            Path to the generated video
        """
        if not self.is_available():
            raise Exception("D-ID API key not configured")
        
        audio_path = kwargs.get("audio_path")
        if not audio_path:
            raise Exception(
                "D-ID requiere audio_path pre-generado. "
                "Genera el audio primero con ElevenLabs y pásalo como audio_path."
            )
        audio_path = Path(audio_path)
        
        image_path = kwargs.get("image_path")
        possible_paths = []
        if not image_path:
            # Buscar en varios lugares
            possible_paths = [
                Path(os.getenv("PAPA_NOEL_IMAGE_PATH", "")),
                Path("assets/Grido_PapaNoel.png"),
                Path("../assets/Grido_PapaNoel.png"),
                Path("grido-backend/assets/Grido_PapaNoel.png"),
                Path("grido-backend/worker/assets/Grido_PapaNoel.png"),
            ]
            for path in possible_paths:
                if path and path.exists():
                    image_path = path
                    break
        else:
            image_path = Path(image_path)
        
        if not image_path or not image_path.exists():
            raise Exception(
                f"Image file not found. Buscado en: {possible_paths if possible_paths else 'paths configurados'}. "
                "Configura PAPA_NOEL_IMAGE_PATH o pasa image_path como parámetro."
            )
        
        try:
            logger.info(f"[D-ID] Subiendo imagen: {image_path}")
            source_url = self._upload_image(image_path)
            
            logger.info(f"[D-ID] Subiendo audio: {audio_path}")
            audio_url = self._upload_audio(audio_path)
            
            logger.info(f"[D-ID] Creando talk...")
            talk_id = self._create_talk(source_url, audio_url)
            
            start_time = time.time()
            while time.time() - start_time < self.max_poll_time:
                status_response = self._poll_talk_status(talk_id)
                
                # D-ID retorna status: "created", "processing", "done", "error"
                status = status_response.get("status")
                
                if status == "done":
                    video_url = (
                        status_response.get("result_url") or
                        status_response.get("url") or
                        status_response.get("video_url")
                    )
                    if not video_url:
                        raise Exception("D-ID talk completed but no video URL provided")
                    
                    logger.info(f"[D-ID] Descargando video: {video_url}")
                    return self._download_video(video_url, output_path)
                
                elif status == "error" or status == "failed":
                        error_obj = status_response.get("error", {})
                        if isinstance(error_obj, dict):
                            error_kind = error_obj.get("kind")
                            error_description = error_obj.get("description") or error_obj.get("message")
                            
                            if error_kind == "FaceError" or (error_description and "face not detected" in str(error_description).lower()):
                                raise Exception(
                                    "D-ID no pudo detectar una cara humana en la imagen. "
                                    "D-ID requiere fotos reales de personas, no funciona con ilustraciones, dibujos o diseños. "
                                    "Si estás usando una imagen de Papá Noel ilustrado, considera usar HeyGen o Higgsfield que soportan avatares personalizados."
                                )
                            else:
                                error_msg = error_description or str(error_obj)
                        else:
                            error_msg = str(error_obj) if error_obj else "Unknown error"
                        
                        if not error_msg or error_msg == "Unknown error":
                            error_msg = str(status_response.get("error", "Unknown error"))
                        
                        raise Exception(f"D-ID video generation failed: {error_msg}")
                
                logger.debug(f"[D-ID] Status: {status}, esperando...")
                time.sleep(self.poll_interval)
            
            raise Exception(f"D-ID video generation timed out after {self.max_poll_time} seconds")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"D-ID API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"D-ID video generation failed: {str(e)}")


"""
Provider Manager with automatic fallback logic.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .base import TTSProvider, LipsyncProvider, VideoProvider
from .kokoro_tts import KokoroTTSProvider
from .elevenlabs_tts import ElevenLabsTTSProvider
from .wav2lip_lipsync import Wav2LipLipsyncProvider
from .synclabs_lipsync import SyncLabsLipsyncProvider
from .heygen_video import HeyGenVideoProvider
from .higgsfield_video import HiggsfieldVideoProvider

# Configure logging
logger = logging.getLogger(__name__)


class ProviderManager:
    """Manages TTS, lip-sync, and video providers with automatic fallback."""
    
    def __init__(self, provider_config=None):
        """
        Initialize provider manager with validated providers.
        
        Args:
            provider_config: ProviderConfig opcional. Si no se proporciona,
                            se valida automáticamente (compatibilidad hacia atrás).
        """
        # Importar configuración de providers
        try:
            from config.providers_config import ProviderConfig, validate_providers
        except ImportError:
            # Fallback para compatibilidad: validar manualmente
            logger.warning("No se pudo importar config.providers_config, usando validación manual")
            provider_config = None
        
        # Usar configuración validada o validar ahora
        if provider_config is None:
            try:
                provider_config = validate_providers()
            except Exception as e:
                logger.error(f"Error validando providers: {e}")
                # Para compatibilidad hacia atrás, intentar inicializar sin validación
                provider_config = None
        
        # Inicializar providers desde configuración validada
        self.provider_config = provider_config
        
        # TTS Providers (para uso en estrategias que requieren TTS)
        self.tts_providers: List[TTSProvider] = []
        if provider_config and provider_config.elevenlabs:
            self.tts_providers.append(provider_config.elevenlabs)
            logger.info("ElevenLabs TTS provider disponible")
        
        # Kokoro (opcional, mantener compatibilidad)
        if not os.getenv("DISABLE_KOKORO", "false").lower() == "true":
            kokoro = KokoroTTSProvider()
            if kokoro.is_available():
                self.tts_providers.append(kokoro)
                logger.info("Kokoro TTS provider disponible")
        
        # Lip-sync Providers (para uso en estrategias que requieren lip-sync)
        self.lipsync_providers: List[LipsyncProvider] = []
        if provider_config:
            if provider_config.wav2lip:
                self.lipsync_providers.append(provider_config.wav2lip)
                logger.info("Wav2Lip lip-sync provider disponible")
        
        # Sync Labs (mantener compatibilidad)
        if not os.getenv("DISABLE_SYNCLABS", "false").lower() == "true":
            synclabs = SyncLabsLipsyncProvider()
            if synclabs.is_available():
                self.lipsync_providers.append(synclabs)
                logger.info("Sync Labs lip-sync provider disponible")
        
        # Video Providers (complete solution - TTS + lip-sync)
        self.video_providers: List[VideoProvider] = []
        if provider_config:
            if provider_config.heygen:
                self.video_providers.append(provider_config.heygen)
                logger.info("HeyGen video provider disponible (Priority 1)")
            if provider_config.higgsfield:
                self.video_providers.append(provider_config.higgsfield)
                logger.info("Higgsfield video provider disponible (Priority 2)")
        
        # Almacenar referencias directas para acceso rápido
        self.heygen = provider_config.heygen if provider_config else None
        self.higgsfield = provider_config.higgsfield if provider_config else None
        self.wav2lip = provider_config.wav2lip if provider_config else None
        self.elevenlabs = provider_config.elevenlabs if provider_config else None
        
        logger.info(
            f"ProviderManager inicializado: {len(self.tts_providers)} TTS, "
            f"{len(self.lipsync_providers)} lip-sync, {len(self.video_providers)} video providers"
        )
    
    def generate_audio_with_fallback(
        self, 
        text: str, 
        output_path: Path, 
        video_id: str = "",
        voice_id: Optional[str] = None,
        use_cache: bool = True
    ) -> Path:
        """
        Generate audio using TTS providers with automatic fallback.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            video_id: Video ID for logging purposes
            voice_id: Voice ID to use (optional)
            use_cache: If True, use audio cache
            
        Returns:
            Path to the generated audio file
            
        Raises:
            Exception: If all TTS providers fail
        """
        if not self.tts_providers:
            raise Exception("No TTS providers available")
        
        # Intentar obtener del caché si está habilitado
        if use_cache:
            try:
                from utils.cache import get_audio_cache
                cache = get_audio_cache()
                provider_name = self.tts_providers[0].__class__.__name__
                cached_audio = cache.get(text, voice_id or "", provider_name)
                if cached_audio:
                    logger.info(f"[{video_id}] Audio obtenido del caché")
                    # Copiar al output_path
                    import shutil
                    shutil.copy2(cached_audio, output_path)
                    return output_path
            except Exception as e:
                logger.warning(f"[{video_id}] Error accediendo al caché: {e}")
        
        last_error = None
        
        for i, provider in enumerate(self.tts_providers):
            provider_name = provider.__class__.__name__
            logger.info(f"[{video_id}] Attempting TTS with {provider_name} (attempt {i+1}/{len(self.tts_providers)})")
            
            try:
                # Pasar voice_id si el provider lo soporta
                if voice_id and hasattr(provider, 'voice_id'):
                    if provider_name == "ElevenLabsTTSProvider":
                        from .elevenlabs_tts import ElevenLabsTTSProvider
                        provider = ElevenLabsTTSProvider(voice_id=voice_id)
                
                result = provider.generate_audio(text, output_path)
                logger.info(f"[{video_id}] Successfully generated audio with {provider_name}")
                
                # Guardar en caché si está habilitado
                if use_cache:
                    try:
                        from utils.cache import get_audio_cache
                        cache = get_audio_cache()
                        cache.put(text, voice_id or "", provider_name, result)
                    except Exception as e:
                        logger.warning(f"[{video_id}] Error guardando en caché: {e}")
                
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"[{video_id}] {provider_name} failed: {str(e)}")
                # Try next provider
                continue
        
        # All providers failed
        raise Exception(f"All TTS providers failed. Last error: {str(last_error)}")
    
    def apply_lipsync_with_fallback(
        self, 
        video: Path, 
        audio: Path, 
        output_path: Path, 
        video_id: str = ""
    ) -> Path:
        """
        Apply lip-sync using providers with automatic fallback.
        
        Args:
            video: Path to the base video (without audio)
            audio: Path to the audio file
            output_path: Path where the video with lip-sync should be saved
            video_id: Video ID for logging purposes
            
        Returns:
            Path to the generated video with lip-sync
            
        Raises:
            Exception: If all lip-sync providers fail
        """
        if not self.lipsync_providers:
            raise Exception("No lip-sync providers available")
        
        last_error = None
        
        for i, provider in enumerate(self.lipsync_providers):
            provider_name = provider.__class__.__name__
            logger.info(
                f"[{video_id}] Attempting lip-sync with {provider_name} "
                f"(attempt {i+1}/{len(self.lipsync_providers)})"
            )
            
            try:
                result = provider.apply_lipsync(video, audio, output_path)
                logger.info(f"[{video_id}] Successfully applied lip-sync with {provider_name}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"[{video_id}] {provider_name} failed: {str(e)}")
                # Try next provider
                continue
        
        # All providers failed
        raise Exception(f"All lip-sync providers failed. Last error: {str(last_error)}")
    
    def generate_video_with_fallback(
        self, 
        script: str, 
        avatar_id: str, 
        output_path: Path, 
        video_id: str = "",
        **kwargs
    ) -> Path:
        """
        Generate complete video using providers with automatic fallback.
        
        Args:
            script: Text script for the video
            avatar_id: ID of the avatar/character to use
            output_path: Path where the video should be saved
            video_id: Video ID for logging purposes
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Path to the generated video
            
        Raises:
            Exception: If all video providers fail
        """
        if not self.video_providers:
            raise Exception("No video providers available")
        
        last_error = None
        
        for i, provider in enumerate(self.video_providers):
            provider_name = provider.__class__.__name__
            logger.info(
                f"[{video_id}] Attempting video generation with {provider_name} "
                f"(attempt {i+1}/{len(self.video_providers)})"
            )
            
            try:
                result = provider.generate_video(script, avatar_id, output_path, **kwargs)
                logger.info(f"[{video_id}] Successfully generated video with {provider_name}")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"[{video_id}] {provider_name} failed: {str(e)}")
                # Try next provider
                continue
        
        # All providers failed
        raise Exception(f"All video providers failed. Last error: {str(last_error)}")
    
    def _compose_videos_with_overlaps(
        self,
        intro_video: Path,
        main_video: Path,
        outro_video: Path,
        output_path: Path,
        video_id: str = "",
        overlap_frames: int = 15,  # ~0.6 segundos a 25fps
    ) -> Path:
        """
        Compone videos con overlaps para transiciones suaves manteniendo transparencia.
        
        Args:
            intro_video: Video intro (Frames_1_2_to_3.mov)
            main_video: Video principal generado (HeyGen o lip-sync)
            outro_video: Video cierre (Frame_4_NocheMagica.mov)
            output_path: Path donde guardar el video final
            video_id: Video ID para logging
            overlap_frames: Número de frames para overlap (default: 15 frames)
            
        Returns:
            Path al video final compuesto
        """
        import subprocess
        import json
        
        logger.info(f"[{video_id}] Componiendo videos con overlaps...")
        
        # Obtener duraciones de los videos
        def get_video_duration(video_path: Path) -> float:
            """Obtiene la duración de un video en segundos."""
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "json", str(video_path)
            ], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        
        def get_video_fps(video_path: Path) -> float:
            """Obtiene el FPS de un video."""
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=r_frame_rate", "-of", "json", str(video_path)
            ], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            rate = data["streams"][0]["r_frame_rate"]
            num, den = map(int, rate.split("/"))
            return num / den if den > 0 else 25.0
        
        intro_duration = get_video_duration(intro_video)
        main_duration = get_video_duration(main_video)
        outro_duration = get_video_duration(outro_video)
        fps = get_video_fps(intro_video)
        
        overlap_seconds = overlap_frames / fps
        
        # Calcular puntos de inicio para overlaps
        # Intro termina en intro_duration
        # Main video empieza en intro_duration - overlap_seconds (overlap con intro)
        # Outro empieza en intro_duration + main_duration - overlap_seconds (overlap con main)
        
        main_start = intro_duration - overlap_seconds
        outro_start = intro_duration + main_duration - overlap_seconds
        total_duration = intro_duration + main_duration + outro_duration - (2 * overlap_seconds)
        
        logger.info(
            f"[{video_id}] Duraciones - Intro: {intro_duration:.2f}s, "
            f"Main: {main_duration:.2f}s, Outro: {outro_duration:.2f}s, "
            f"Overlap: {overlap_seconds:.2f}s, Total: {total_duration:.2f}s"
        )
        
        # Verificar qué videos tienen audio
        def has_audio_stream(video_path: Path) -> bool:
            """Verifica si un video tiene stream de audio."""
            result = subprocess.run([
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "stream=codec_type", "-of", "json",
                str(video_path)
            ], capture_output=True, text=True)
            return "codec_type" in result.stdout
        
        intro_has_audio = has_audio_stream(intro_video)
        main_has_audio = has_audio_stream(main_video)
        outro_has_audio = has_audio_stream(outro_video)
        
        logger.info(
            f"[{video_id}] Audio streams - Intro: {intro_has_audio}, "
            f"Main: {main_has_audio}, Outro: {outro_has_audio}"
        )
        
        # Crear filtro complejo de FFmpeg para composición con overlaps y transparencia
        # Optimizado: usar Lanczos scaling para mejor calidad, mantener transparencia
        # Usamos overlay con alpha para mantener transparencia en .mov
        video_filter = (
            f"[0:v] setpts=PTS-STARTPTS, scale=1080:1920:flags=lanczos [intro]; "
            f"[1:v] setpts=PTS-STARTPTS, scale=1080:1920:flags=lanczos [main]; "
            f"[2:v] setpts=PTS-STARTPTS, scale=1080:1920:flags=lanczos [outro]; "
            f"[intro][main] overlay=0:0:enable='between(t,{main_start},{intro_duration})':alpha=premultiplied [tmp1]; "
            f"[tmp1][outro] overlay=0:0:enable='between(t,{outro_start},{intro_duration + main_duration})':alpha=premultiplied [v]"
        )
        
        # Construir filtro de audio solo para videos que tienen audio
        audio_filters = []
        audio_mix_inputs = []
        input_idx = 0
        
        # Mejorar sincronización de audio: usar asetpts para alinear correctamente
        if intro_has_audio:
            # Audio del intro empieza en t=0, sin delay
            audio_filters.append(f"[0:a] asetpts=PTS-STARTPTS, adelay=0|0 [a0]")
            audio_mix_inputs.append("[a0]")
            input_idx += 1
        
        if main_has_audio:
            # Audio del main video debe empezar cuando el main video empieza
            # main_start puede ser negativo (overlap), ajustar a 0 si es negativo
            delay_start = max(0, main_start)
            delay_ms = int(delay_start * 1000)
            # Usar asetpts para resetear timestamps y luego aplicar delay
            audio_filters.append(f"[1:a] asetpts=PTS-STARTPTS, adelay={delay_ms}|{delay_ms} [a1]")
            audio_mix_inputs.append("[a1]")
            input_idx += 1
        
        if outro_has_audio:
            # Audio del outro debe empezar cuando el outro empieza
            delay_start = max(0, outro_start)
            delay_ms = int(delay_start * 1000)
            audio_filters.append(f"[2:a] asetpts=PTS-STARTPTS, adelay={delay_ms}|{delay_ms} [a2]")
            audio_mix_inputs.append("[a2]")
            input_idx += 1
        
        # Construir filtro completo
        if audio_filters and audio_mix_inputs:
            audio_filter = "; ".join(audio_filters)
            mix_filter = f"{' '.join(audio_mix_inputs)} amix=inputs={len(audio_mix_inputs)}:duration=longest:dropout_transition=0 [a]"
            filter_complex = f"{video_filter}; {audio_filter}; {mix_filter}"
        else:
            # Si no hay audio, solo video
            filter_complex = video_filter
        
        # Ejecutar FFmpeg con composición
        # Usar pix_fmt con alpha para mantener transparencia
        cmd = [
            "ffmpeg",
            "-i", str(intro_video),
            "-i", str(main_video),
            "-i", str(outro_video),
            "-filter_complex", filter_complex,
            "-map", "[v]",
        ]
        
        # Agregar audio solo si hay streams de audio
        if audio_filters and audio_mix_inputs:
            cmd.extend(["-map", "[a]"])
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-an"])  # Sin audio
        
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",  # Balance entre velocidad y calidad
            "-crf", "23",  # Calidad constante (18-28, menor = mejor calidad)
            "-pix_fmt", "yuv420p",  # Compatibilidad universal
            "-movflags", "+faststart",  # Optimización para streaming
            "-profile:v", "high",  # Perfil H.264 high para mejor calidad
            "-level", "4.0",  # Nivel H.264
            "-t", str(total_duration),
            "-y", str(output_path)
        ])
        
        logger.info(f"[{video_id}] Ejecutando FFmpeg con overlaps...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"[{video_id}] FFmpeg error: {result.stderr}")
            raise Exception(f"FFmpeg composition failed: {result.stderr}")
        
        logger.info(f"[{video_id}] ✅ Videos compuestos con overlaps")
        return output_path
    
    def _process_with_heygen(
        self,
        intro_video: Path,
        outro_video: Path,
        script_frame2: str,
        script_frame3: str,
        temp_dir: Path,
        video_id: str = "",
    ) -> Path:
        """
        Procesa video usando HeyGen (video completo con TTS + lip-sync integrado).
        
        Args:
            intro_video: Path al video intro
            outro_video: Path al video outro
            script_frame2: Script para frame 2 (VO intro)
            script_frame3: Script para frame 3 (diálogo principal)
            temp_dir: Directorio temporal para archivos intermedios
            video_id: ID del video para logging
            
        Returns:
            Path al video final compuesto
            
        Raises:
            Exception: Si HeyGen no está disponible o falla
        """
        import subprocess
        import sys
        
        if not self.heygen:
            raise Exception("HeyGen no está disponible")
        
        logger.info(f"[{video_id}] Procesando con HeyGen...")
        
        # Importar configuración de Papá Noel
        worker_dir = Path(__file__).parent.parent.parent
        if str(worker_dir) not in sys.path:
            sys.path.insert(0, str(worker_dir))
        from papa_noel_config import (
            get_papa_noel_avatar_id, 
            get_papa_noel_voice_id_heygen,
            get_papa_noel_voice_id_elevenlabs
        )
        
        # Generar video completo con HeyGen
        main_video_path = temp_dir / "main_video_heygen.mov"
        main_video = self.heygen.generate_video(
            script_frame3,
            avatar_id=get_papa_noel_avatar_id(),
            output_path=main_video_path,
            voice_id=get_papa_noel_voice_id_heygen(),  # Usar voice_id específico de HeyGen
        )
        
        # Generar audio para frame 2 (VO para el intro) usando ElevenLabs
        # Usar voice_id específico de ElevenLabs
        audio_frame2_path = temp_dir / "audio_frame2.wav"
        audio_frame2 = self.generate_audio_with_fallback(
            script_frame2, 
            audio_frame2_path, 
            video_id,
            voice_id=get_papa_noel_voice_id_elevenlabs()  # Usar voice_id específico de ElevenLabs
        )
        
        # Agregar audio al intro
        intro_with_audio_path = temp_dir / "intro_with_audio.mov"
        subprocess.run([
            "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y", str(intro_with_audio_path)
        ], check=True, capture_output=True)
        
        # Componer con overlaps
        output_path = temp_dir / "video_final_heygen.mp4"
        return self._compose_videos_with_overlaps(
            intro_with_audio_path,
            main_video,
            outro_video,
            output_path,
            video_id,
        )
    
    def _process_with_higgsfield(
        self,
        intro_video: Path,
        outro_video: Path,
        script_frame2: str,
        script_frame3: str,
        temp_dir: Path,
        video_id: str = "",
    ) -> Path:
        """
        Procesa video usando Higgsfield (video completo con TTS + lip-sync integrado).
        
        Args:
            intro_video: Path al video intro
            outro_video: Path al video outro
            script_frame2: Script para frame 2 (VO intro)
            script_frame3: Script para frame 3 (diálogo principal)
            temp_dir: Directorio temporal para archivos intermedios
            video_id: ID del video para logging
            
        Returns:
            Path al video final compuesto
            
        Raises:
            Exception: Si Higgsfield no está disponible o falla
        """
        import subprocess
        import sys
        
        if not self.higgsfield:
            raise Exception("Higgsfield no está disponible")
        
        logger.info(f"[{video_id}] Procesando con Higgsfield...")
        
        # Importar configuración de Papá Noel
        worker_dir = Path(__file__).parent.parent.parent
        if str(worker_dir) not in sys.path:
            sys.path.insert(0, str(worker_dir))
        from papa_noel_config import get_papa_noel_avatar_id
        
        # Generar video completo con Higgsfield
        main_video_path = temp_dir / "main_video_higgsfield.mov"
        main_video = self.higgsfield.generate_video(
            script_frame3,
            avatar_id=get_papa_noel_avatar_id(),
            output_path=main_video_path,
        )
        
        # Generar audio para frame 2 (VO para el intro)
        audio_frame2_path = temp_dir / "audio_frame2.wav"
        audio_frame2 = self.generate_audio_with_fallback(
            script_frame2, audio_frame2_path, video_id
        )
        
        # Agregar audio al intro
        intro_with_audio_path = temp_dir / "intro_with_audio.mov"
        subprocess.run([
            "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y", str(intro_with_audio_path)
        ], check=True, capture_output=True)
        
        # Componer con overlaps
        output_path = temp_dir / "video_final_higgsfield.mp4"
        return self._compose_videos_with_overlaps(
            intro_with_audio_path,
            main_video,
            outro_video,
            output_path,
            video_id,
        )
    
    def _process_with_wav2lip(
        self,
        intro_video: Path,
        base_video: Path,
        outro_video: Path,
        script_frame2: str,
        script_frame3: str,
        temp_dir: Path,
        video_id: str = "",
    ) -> Path:
        """
        Procesa video usando Wav2Lip (TTS con ElevenLabs + lip-sync con Wav2Lip).
        
        Args:
            intro_video: Path al video intro
            base_video: Path al video base (frame 3 - Santa)
            outro_video: Path al video outro
            script_frame2: Script para frame 2 (VO intro)
            script_frame3: Script para frame 3 (diálogo principal)
            temp_dir: Directorio temporal para archivos intermedios
            video_id: ID del video para logging
            
        Returns:
            Path al video final compuesto
            
        Raises:
            Exception: Si Wav2Lip o ElevenLabs no están disponibles o fallan
        """
        import subprocess
        
        if not self.wav2lip:
            raise Exception("Wav2Lip no está disponible")
        if not self.elevenlabs:
            raise Exception("ElevenLabs no está disponible (requerido para TTS)")
        
        logger.info(f"[{video_id}] Procesando con Wav2Lip + ElevenLabs...")
        
        # Importar configuración de Papá Noel para voice_id de ElevenLabs
        worker_dir = Path(__file__).parent.parent.parent
        if str(worker_dir) not in sys.path:
            sys.path.insert(0, str(worker_dir))
        from papa_noel_config import get_papa_noel_voice_id_elevenlabs
        
        # Generar audio para frame 2 (VO para el intro) usando voice_id específico de ElevenLabs
        audio_frame2_path = temp_dir / "audio_frame2.wav"
        audio_frame2 = self.generate_audio_with_fallback(
            script_frame2, 
            audio_frame2_path, 
            video_id,
            voice_id=get_papa_noel_voice_id_elevenlabs()
        )
        
        # Generar audio para frame 3 usando voice_id específico de ElevenLabs
        audio_frame3_path = temp_dir / "audio_frame3.wav"
        audio_frame3 = self.generate_audio_with_fallback(
            script_frame3, 
            audio_frame3_path, 
            video_id,
            voice_id=get_papa_noel_voice_id_elevenlabs()
        )
        
        # Aplicar lip-sync con Wav2Lip
        frame3_lipsync_path = temp_dir / "frame3_lipsync_wav2lip.mov"
        frame3_lipsync = self.wav2lip.apply_lipsync(
            base_video, audio_frame3, frame3_lipsync_path
        )
        
        # Agregar audio al intro
        intro_with_audio_path = temp_dir / "intro_with_audio.mov"
        subprocess.run([
            "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-y", str(intro_with_audio_path)
        ], check=True, capture_output=True)
        
        # Componer con overlaps
        output_path = temp_dir / "video_final_wav2lip.mp4"
        return self._compose_videos_with_overlaps(
            intro_with_audio_path,
            frame3_lipsync,
            outro_video,
            output_path,
            video_id,
        )
    
    def _process_with_elevenlabs(
        self,
        intro_video: Path,
        base_video: Path,
        outro_video: Path,
        script_frame2: str,
        script_frame3: str,
        temp_dir: Path,
        video_id: str = "",
    ) -> Path:
        """
        Procesa video usando ElevenLabs (TTS + base video sin lip-sync - fallback final).
        
        Args:
            intro_video: Path al video intro
            base_video: Path al video base (frame 3 - Santa)
            outro_video: Path al video outro
            script_frame2: Script para frame 2 (VO intro)
            script_frame3: Script para frame 3 (diálogo principal)
            temp_dir: Directorio temporal para archivos intermedios
            video_id: ID del video para logging
            
        Returns:
            Path al video final compuesto
            
        Raises:
            Exception: Si ElevenLabs no está disponible o falla
        """
        import subprocess
        import json as json_module
        
        if not self.elevenlabs:
            raise Exception("ElevenLabs no está disponible")
        
        logger.info(f"[{video_id}] Procesando con ElevenLabs (fallback final - sin lip-sync)...")
        
        # Importar configuración de Papá Noel para voice_id de ElevenLabs
        worker_dir = Path(__file__).parent.parent.parent
        if str(worker_dir) not in sys.path:
            sys.path.insert(0, str(worker_dir))
        from papa_noel_config import get_papa_noel_voice_id_elevenlabs
        
        # Generar audio para frame 2 (VO para el intro) usando voice_id específico de ElevenLabs
        audio_frame2_path = temp_dir / "audio_frame2.wav"
        audio_frame2 = self.generate_audio_with_fallback(
            script_frame2, 
            audio_frame2_path, 
            video_id,
            voice_id=get_papa_noel_voice_id_elevenlabs()
        )
        
        # Generar audio para frame 3 usando voice_id específico de ElevenLabs
        audio_frame3_path = temp_dir / "audio_frame3.wav"
        audio_frame3 = self.generate_audio_with_fallback(
            script_frame3, 
            audio_frame3_path, 
            video_id,
            voice_id=get_papa_noel_voice_id_elevenlabs()
        )
        
        # Agregar audio al intro
        intro_with_audio_path = temp_dir / "intro_with_audio.mov"
        subprocess.run([
            "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-y", str(intro_with_audio_path)
        ], check=True, capture_output=True)
        
        # Agregar audio al video base (sin lip-sync)
        frame3_with_audio_path = temp_dir / "frame3_with_audio.mov"
        
        # Obtener duraciones para sincronizar
        audio_duration_result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(audio_frame3)
        ], capture_output=True, text=True, check=True)
        audio_duration = float(json_module.loads(audio_duration_result.stdout)["format"]["duration"])
        
        video_duration_result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(base_video)
        ], capture_output=True, text=True, check=True)
        video_duration = float(json_module.loads(video_duration_result.stdout)["format"]["duration"])
        
        final_duration = min(audio_duration, video_duration)
        
        subprocess.run([
            "ffmpeg",
            "-i", str(base_video),
            "-i", str(audio_frame3),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            "-pix_fmt", "yuv420p",
            "-t", str(final_duration),
            "-y", str(frame3_with_audio_path)
        ], check=True, capture_output=True)
        
        # Componer con overlaps
        output_path = temp_dir / "video_final_elevenlabs.mp4"
        return self._compose_videos_with_overlaps(
            intro_with_audio_path,
            frame3_with_audio_path,
            outro_video,
            output_path,
            video_id,
        )
    
    def process_video_with_fallback(
        self,
        intro_video: Path,
        base_video: Path,
        outro_video: Path,
        script_frame2: str,
        script_frame3: str,
        output_path: Path,
        video_id: str = "",
    ) -> Path:
        """
        Process complete video con fallback automático en orden de prioridad.
        
        Orden de prioridad:
        1. HeyGen (Video completo - TTS + lip-sync integrado)
        2. Higgsfield (Video completo - TTS + lip-sync integrado)
        3. Wav2Lip (TTS con ElevenLabs + lip-sync con Wav2Lip)
        4. ElevenLabs (TTS + base video sin lip-sync - fallback final)
        
        Este método implementa la composición con overlaps según las especificaciones:
        - Intro: Frames_1_2_to_3.mov con audio agregado
        - Main: Video generado por provider seleccionado (con overlap al final del intro)
        - Outro: Frame_4_NocheMagica.mov (con overlap al final del main)
        
        Args:
            intro_video: Path to intro video (Frames_1_2_to_3.mov)
            base_video: Path to base video (frame 3 - Santa) - usado en Wav2Lip, ElevenLabs
            outro_video: Path to outro video (Frame_4_NocheMagica.mov)
            script_frame2: Script for frame 2 audio (VO de Papá Noel para el intro)
            script_frame3: Script for frame 3 (main dialogue)
            output_path: Path where final video should be saved
            video_id: Video ID for logging purposes
            
        Returns:
            Path to the final composed video with overlaps
            
        Raises:
            Exception: Si todos los providers fallan
        """
        temp_dir = output_path.parent / f"temp_{video_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        last_error = None
        strategies_tried = []
        
        # Estrategia 1: HeyGen (Video completo)
        if self.heygen:
            try:
                logger.info(f"[{video_id}] Intentando con HeyGen (Priority 1)...")
                result = self._process_with_heygen(
                    intro_video, outro_video, script_frame2, script_frame3,
                    temp_dir, video_id
                )
                # Copiar resultado al output_path final
                import shutil
                shutil.copy2(result, output_path)
                logger.info(f"[{video_id}] ✅ Video generado exitosamente con HeyGen")
                return output_path
            except Exception as e:
                last_error = e
                strategies_tried.append("HeyGen")
                logger.warning(f"[{video_id}] HeyGen falló: {str(e)}")
        
        # Estrategia 2: Higgsfield (Video completo)
        if self.higgsfield:
            try:
                logger.info(f"[{video_id}] Intentando con Higgsfield (Priority 2)...")
                result = self._process_with_higgsfield(
                    intro_video, outro_video, script_frame2, script_frame3,
                    temp_dir, video_id
                )
                import shutil
                shutil.copy2(result, output_path)
                logger.info(f"[{video_id}] ✅ Video generado exitosamente con Higgsfield")
                return output_path
            except Exception as e:
                last_error = e
                strategies_tried.append("Higgsfield")
                logger.warning(f"[{video_id}] Higgsfield falló: {str(e)}")
        
        # Estrategia 3: Wav2Lip (TTS + lip-sync)
        if self.wav2lip and self.elevenlabs:
            try:
                logger.info(f"[{video_id}] Intentando con Wav2Lip + ElevenLabs (Priority 3)...")
                result = self._process_with_wav2lip(
                    intro_video, base_video, outro_video, script_frame2, script_frame3,
                    temp_dir, video_id
                )
                import shutil
                shutil.copy2(result, output_path)
                logger.info(f"[{video_id}] ✅ Video generado exitosamente con Wav2Lip")
                return output_path
            except Exception as e:
                last_error = e
                strategies_tried.append("Wav2Lip")
                logger.warning(f"[{video_id}] Wav2Lip falló: {str(e)}")
        
        # Estrategia 4: ElevenLabs (TTS + base video - fallback final)
        if self.elevenlabs:
            try:
                logger.info(f"[{video_id}] Intentando con ElevenLabs (Priority 4 - fallback final)...")
                result = self._process_with_elevenlabs(
                    intro_video, base_video, outro_video, script_frame2, script_frame3,
                    temp_dir, video_id
                )
                import shutil
                shutil.copy2(result, output_path)
                logger.info(f"[{video_id}] ✅ Video generado exitosamente con ElevenLabs (sin lip-sync)")
                return output_path
            except Exception as e:
                last_error = e
                strategies_tried.append("ElevenLabs")
                logger.error(f"[{video_id}] ElevenLabs falló: {str(e)}")
        
        # Si llegamos aquí, todos los providers fallaron
        error_msg = (
            f"Todos los providers fallaron. Estrategias intentadas: {', '.join(strategies_tried) if strategies_tried else 'ninguna'}.\n"
            f"Último error: {str(last_error) if last_error else 'No hay providers disponibles'}"
        )
        logger.error(f"[{video_id}] ❌ {error_msg}")
        raise Exception(error_msg)


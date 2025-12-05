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
from .musetalk_lipsync import MuseTalkLipsyncProvider
from .wav2lip_lipsync import Wav2LipLipsyncProvider
from .synclabs_lipsync import SyncLabsLipsyncProvider
from .heygen_video import HeyGenVideoProvider
from .higgsfield_video import HiggsfieldVideoProvider

# Configure logging
logger = logging.getLogger(__name__)


class ProviderManager:
    """Manages TTS, lip-sync, and video providers with automatic fallback."""
    
    def __init__(self):
        """Initialize provider manager with all available providers."""
        # TTS Providers (in order of preference)
        self.tts_providers: List[TTSProvider] = []
        
        # Check if providers are disabled via environment variables
        if not os.getenv("DISABLE_KOKORO", "false").lower() == "true":
            kokoro = KokoroTTSProvider()
            if kokoro.is_available():
                self.tts_providers.append(kokoro)
                logger.info("Kokoro TTS provider available")
        
        if not os.getenv("DISABLE_ELEVENLABS", "false").lower() == "true":
            elevenlabs = ElevenLabsTTSProvider()
            if elevenlabs.is_available():
                self.tts_providers.append(elevenlabs)
                logger.info("ElevenLabs TTS provider available")
        
        # Lip-sync Providers (in order of preference)
        self.lipsync_providers: List[LipsyncProvider] = []
        
        # MuseTalk (preferred - faster and more accurate)
        if not os.getenv("DISABLE_MUSETALK", "false").lower() == "true":
            musetalk = MuseTalkLipsyncProvider()
            if musetalk.is_available():
                self.lipsync_providers.append(musetalk)
                logger.info("MuseTalk lip-sync provider available")
        
        # Sync Labs (commercial HD version - preferred if available)
        if not os.getenv("DISABLE_SYNCLABS", "false").lower() == "true":
            synclabs = SyncLabsLipsyncProvider()
            if synclabs.is_available():
                self.lipsync_providers.append(synclabs)
                logger.info("Sync Labs lip-sync provider available")
        
        # Wav2Lip (fallback - open-source alternative)
        if not os.getenv("DISABLE_WAV2LIP", "false").lower() == "true":
            wav2lip = Wav2LipLipsyncProvider()
            if wav2lip.is_available():
                self.lipsync_providers.append(wav2lip)
                logger.info("Wav2Lip lip-sync provider available")
        
        # Video Providers (complete solution - TTS + lip-sync)
        self.video_providers: List[VideoProvider] = []
        
        # Higgsfield (nuevo provider)
        if not os.getenv("DISABLE_HIGGSFIELD", "false").lower() == "true":
            higgsfield = HiggsfieldVideoProvider()
            if higgsfield.is_available():
                self.video_providers.append(higgsfield)
                logger.info("Higgsfield video provider available")
        
        if not os.getenv("DISABLE_HEYGEN", "false").lower() == "true":
            heygen = HeyGenVideoProvider()
            if heygen.is_available():
                self.video_providers.append(heygen)
                logger.info("HeyGen video provider available")
        
        logger.info(
            f"ProviderManager initialized: {len(self.tts_providers)} TTS, "
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
        
        if intro_has_audio:
            audio_filters.append(f"[0:a] adelay={0}|{0} [a0]")
            audio_mix_inputs.append("[a0]")
            input_idx += 1
        
        if main_has_audio:
            delay_ms = int(main_start * 1000)
            audio_filters.append(f"[1:a] adelay={delay_ms}|{delay_ms} [a1]")
            audio_mix_inputs.append("[a1]")
            input_idx += 1
        
        if outro_has_audio:
            delay_ms = int(outro_start * 1000)
            audio_filters.append(f"[2:a] adelay={delay_ms}|{delay_ms} [a2]")
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
        Process complete video with TTS + lip-sync, falling back to complete video providers if needed.
        
        Este método implementa la composición con overlaps según las especificaciones:
        - Intro: Frames_1_2_to_3.mov con audio agregado
        - Main: Video generado por HeyGen o lip-sync (con overlap al final del intro)
        - Outro: Frame_4_NocheMagica.mov (con overlap al final del main)
        
        Args:
            intro_video: Path to intro video (Frames_1_2_to_3.mov)
            base_video: Path to base video (frame 3 - Santa) - solo usado en Strategy 1
            outro_video: Path to outro video (Frame_4_NocheMagica.mov)
            script_frame2: Script for frame 2 audio (VO de Papá Noel para el intro)
            script_frame3: Script for frame 3 (main dialogue)
            output_path: Path where final video should be saved
            video_id: Video ID for logging purposes
            
        Returns:
            Path to the final composed video with overlaps
        """
        from pathlib import Path
        import subprocess
        
        temp_dir = output_path.parent / f"temp_{video_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Strategy 1: Try TTS + lip-sync approach
            try:
                logger.info(f"[{video_id}] Attempting Strategy 1: TTS + lip-sync")
                
                # Generate audio for frame 2 (VO para el intro)
                audio_frame2_path = temp_dir / "audio_frame2.wav"
                audio_frame2 = self.generate_audio_with_fallback(
                    script_frame2, audio_frame2_path, video_id
                )
                
                # Generate audio for frame 3
                audio_frame3_path = temp_dir / "audio_frame3.wav"
                audio_frame3 = self.generate_audio_with_fallback(
                    script_frame3, audio_frame3_path, video_id
                )
                
                # Apply lip-sync to frame 3
                frame3_lipsync_path = temp_dir / "frame3_lipsync.mov"
                frame3_lipsync = self.apply_lipsync_with_fallback(
                    base_video, audio_frame3, frame3_lipsync_path, video_id
                )
                
                # Add audio to intro (mantener formato .mov para transparencia)
                intro_with_audio_path = temp_dir / "intro_with_audio.mov"
                subprocess.run([
                    "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-y", str(intro_with_audio_path)
                ], check=True, capture_output=True)
                
                # Componer con overlaps
                return self._compose_videos_with_overlaps(
                    intro_with_audio_path,
                    frame3_lipsync,
                    outro_video,
                    output_path,
                    video_id,
                )
                
            except Exception as e:
                logger.warning(f"[{video_id}] Strategy 1 failed: {str(e)}")
                logger.info(f"[{video_id}] Falling back to Strategy 2: Complete video generation (HeyGen)")
                
                # Strategy 2: Use complete video provider (HeyGen)
                try:
                    # Generate full script (solo frame 3, el frame 2 se agrega al intro)
                    # Nota: HeyGen generará solo el video principal de Papá Noel hablando
                    
                    # Generate complete video with HeyGen (solo el diálogo principal)
                    heygen_output = temp_dir / "heygen_video.mov"
                    heygen_video = self.generate_video_with_fallback(
                        script_frame3,  # Solo el script principal
                        avatar_id="santa",  # Default avatar
                        output_path=heygen_output,
                        video_id=video_id,
                    )
                    
                    # Agregar audio al intro (VO de Papá Noel)
                    audio_frame2_path = temp_dir / "audio_frame2.wav"
                    audio_frame2 = self.generate_audio_with_fallback(
                        script_frame2, audio_frame2_path, video_id
                    )
                    
                    intro_with_audio_path = temp_dir / "intro_with_audio.mov"
                    subprocess.run([
                        "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                        "-y", str(intro_with_audio_path)
                    ], check=True, capture_output=True)
                    
                    # Componer con overlaps
                    return self._compose_videos_with_overlaps(
                        intro_with_audio_path,
                        heygen_video,
                        outro_video,
                        output_path,
                        video_id,
                    )
                    
                except Exception as e2:
                    logger.warning(f"[{video_id}] Strategy 2 failed: {str(e2)}")
                    logger.info(f"[{video_id}] Falling back to Strategy 3: TTS + base video (no lip-sync)")
                    
                    # Strategy 3: TTS + base video (sin lip-sync) - fallback cuando todo falla
                    # Esta es la opción más básica pero funcional: solo agregamos audio al video base
                    
                    # Generate audio for frame 2 (VO para el intro)
                    audio_frame2_path = temp_dir / "audio_frame2.wav"
                    audio_frame2 = self.generate_audio_with_fallback(
                        script_frame2, audio_frame2_path, video_id
                    )
                    
                    # Generate audio for frame 3
                    audio_frame3_path = temp_dir / "audio_frame3.wav"
                    audio_frame3 = self.generate_audio_with_fallback(
                        script_frame3, audio_frame3_path, video_id
                    )
                    
                    # Add audio to intro
                    intro_with_audio_path = temp_dir / "intro_with_audio.mov"
                    subprocess.run([
                        "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k", "-shortest",
                        "-pix_fmt", "yuv420p",
                        "-y", str(intro_with_audio_path)
                    ], check=True, capture_output=True)
                    
                    # Add audio to frame3 base video (sin lip-sync, solo audio sobre video)
                    frame3_with_audio_path = temp_dir / "frame3_with_audio.mov"
                    subprocess.run([
                        "ffmpeg", "-i", str(base_video), "-i", str(audio_frame3),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k", "-shortest",
                        "-pix_fmt", "yuv420p",
                        "-y", str(frame3_with_audio_path)
                    ], check=True, capture_output=True)
                    
                    # Componer con overlaps
                    return self._compose_videos_with_overlaps(
                        intro_with_audio_path,
                        frame3_with_audio_path,
                        outro_video,
                        output_path,
                        video_id,
                    )
                
        finally:
            # Cleanup temp directory (optional - comment out for debugging)
            # import shutil
            # shutil.rmtree(temp_dir, ignore_errors=True)
            pass


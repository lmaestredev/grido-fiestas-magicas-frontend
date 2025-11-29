"""
Provider Manager with automatic fallback logic.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

from .base import TTSProvider, LipsyncProvider, VideoProvider
from .kokoro_tts import KokoroTTSProvider
from .elevenlabs_tts import ElevenLabsTTSProvider
from .musetalk_lipsync import MuseTalkLipsyncProvider
from .heygen_video import HeyGenVideoProvider

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
        
        if not os.getenv("DISABLE_MUSETALK", "false").lower() == "true":
            musetalk = MuseTalkLipsyncProvider()
            if musetalk.is_available():
                self.lipsync_providers.append(musetalk)
                logger.info("MuseTalk lip-sync provider available")
        
        # Video Providers (complete solution - TTS + lip-sync)
        self.video_providers: List[VideoProvider] = []
        
        if not os.getenv("DISABLE_HEYGEN", "false").lower() == "true":
            heygen = HeyGenVideoProvider()
            if heygen.is_available():
                self.video_providers.append(heygen)
                logger.info("HeyGen video provider available")
        
        logger.info(
            f"ProviderManager initialized: {len(self.tts_providers)} TTS, "
            f"{len(self.lipsync_providers)} lip-sync, {len(self.video_providers)} video providers"
        )
    
    def generate_audio_with_fallback(self, text: str, output_path: Path, video_id: str = "") -> Path:
        """
        Generate audio using TTS providers with automatic fallback.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            video_id: Video ID for logging purposes
            
        Returns:
            Path to the generated audio file
            
        Raises:
            Exception: If all TTS providers fail
        """
        if not self.tts_providers:
            raise Exception("No TTS providers available")
        
        last_error = None
        
        for i, provider in enumerate(self.tts_providers):
            provider_name = provider.__class__.__name__
            logger.info(f"[{video_id}] Attempting TTS with {provider_name} (attempt {i+1}/{len(self.tts_providers)})")
            
            try:
                result = provider.generate_audio(text, output_path)
                logger.info(f"[{video_id}] Successfully generated audio with {provider_name}")
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
        
        This is the main method that implements the full fallback strategy:
        1. Try Kokoro TTS + MuseTalk lip-sync
        2. Try ElevenLabs TTS + MuseTalk lip-sync
        3. Try HeyGen (complete video generation)
        
        Args:
            intro_video: Path to intro video
            base_video: Path to base video (frame 3 - Santa)
            outro_video: Path to outro video
            script_frame2: Script for frame 2 audio
            script_frame3: Script for frame 3 (main dialogue)
            output_path: Path where final video should be saved
            video_id: Video ID for logging purposes
            
        Returns:
            Path to the final concatenated video
        """
        from pathlib import Path
        import subprocess
        
        temp_dir = output_path.parent / f"temp_{video_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Strategy 1: Try TTS + lip-sync approach
            try:
                logger.info(f"[{video_id}] Attempting Strategy 1: TTS + lip-sync")
                
                # Generate audio for frame 2
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
                frame3_lipsync_path = temp_dir / "frame3_lipsync.mp4"
                frame3_lipsync = self.apply_lipsync_with_fallback(
                    base_video, audio_frame3, frame3_lipsync_path, video_id
                )
                
                # Add audio to intro
                intro_with_audio_path = temp_dir / "intro_with_audio.mp4"
                subprocess.run([
                    "ffmpeg", "-i", str(intro_video), "-i", str(audio_frame2),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    "-y", str(intro_with_audio_path)
                ], check=True, capture_output=True)
                
                # Concatenate videos
                concat_list = temp_dir / "concat_list.txt"
                with open(concat_list, "w") as f:
                    f.write(f"file '{intro_with_audio_path.absolute()}'\n")
                    f.write(f"file '{frame3_lipsync.absolute()}'\n")
                    f.write(f"file '{outro_video.absolute()}'\n")
                
                # Try concatenation without re-encoding
                result = subprocess.run([
                    "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-c", "copy", "-y", str(output_path)
                ], capture_output=True)
                
                # If that fails, re-encode
                if result.returncode != 0:
                    subprocess.run([
                        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-c:a", "aac", "-b:a", "128k", "-y", str(output_path)
                    ], check=True, capture_output=True)
                
                logger.info(f"[{video_id}] Strategy 1 succeeded: TTS + lip-sync")
                return output_path
                
            except Exception as e:
                logger.warning(f"[{video_id}] Strategy 1 failed: {str(e)}")
                logger.info(f"[{video_id}] Falling back to Strategy 2: Complete video generation")
                
                # Strategy 2: Use complete video provider (HeyGen)
                # Generate full script
                full_script = f"{script_frame2}\n\n{script_frame3}"
                
                # Generate complete video with HeyGen
                heygen_output = temp_dir / "heygen_video.mp4"
                heygen_video = self.generate_video_with_fallback(
                    full_script,
                    avatar_id="santa",  # Default avatar
                    output_path=heygen_output,
                    video_id=video_id,
                )
                
                # Copy to final output
                import shutil
                shutil.copy2(heygen_video, output_path)
                
                logger.info(f"[{video_id}] Strategy 2 succeeded: Complete video generation")
                return output_path
                
        finally:
            # Cleanup temp directory (optional - comment out for debugging)
            # import shutil
            # shutil.rmtree(temp_dir, ignore_errors=True)
            pass


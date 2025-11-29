"""
Base classes for TTS, lip-sync, and video providers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TTSProvider(ABC):
    """Base class for Text-to-Speech providers."""
    
    @abstractmethod
    def generate_audio(self, text: str, output_path: Path) -> Path:
        """
        Generate audio from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path where the audio file should be saved
            
        Returns:
            Path to the generated audio file
            
        Raises:
            Exception: If audio generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if the provider can be used, False otherwise
        """
        pass


class LipsyncProvider(ABC):
    """Base class for lip-sync providers."""
    
    @abstractmethod
    def apply_lipsync(self, video: Path, audio: Path, output_path: Path) -> Path:
        """
        Apply lip-sync to a video using audio.
        
        Args:
            video: Path to the base video (without audio)
            audio: Path to the audio file
            output_path: Path where the video with lip-sync should be saved
            
        Returns:
            Path to the generated video with lip-sync
            
        Raises:
            Exception: If lip-sync application fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if the provider can be used, False otherwise
        """
        pass


class VideoProvider(ABC):
    """Base class for complete video generation providers (TTS + lip-sync)."""
    
    @abstractmethod
    def generate_video(self, script: str, avatar_id: str, output_path: Path, **kwargs) -> Path:
        """
        Generate a complete video with TTS and lip-sync.
        
        Args:
            script: Text script for the video
            avatar_id: ID of the avatar/character to use
            output_path: Path where the video should be saved
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Path to the generated video
            
        Raises:
            Exception: If video generation fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and configured.
        
        Returns:
            True if the provider can be used, False otherwise
        """
        pass


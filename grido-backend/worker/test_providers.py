"""
Test script for validating all providers.
"""

import os
import sys
from pathlib import Path
import logging

# Add providers to path
sys.path.insert(0, str(Path(__file__).parent))

from providers.manager import ProviderManager
from providers.kokoro_tts import KokoroTTSProvider
from providers.elevenlabs_tts import ElevenLabsTTSProvider
from providers.musetalk_lipsync import MuseTalkLipsyncProvider
from providers.heygen_video import HeyGenVideoProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_tts_provider(provider, text: str, output_path: Path):
    """Test a TTS provider."""
    provider_name = provider.__class__.__name__
    logger.info(f"Testing {provider_name}...")
    
    if not provider.is_available():
        logger.warning(f"{provider_name} is not available (skipping)")
        return False
    
    try:
        result = provider.generate_audio(text, output_path)
        if result.exists():
            logger.info(f"✅ {provider_name} succeeded: {result}")
            return True
        else:
            logger.error(f"❌ {provider_name} failed: Output file not found")
            return False
    except Exception as e:
        logger.error(f"❌ {provider_name} failed: {str(e)}")
        return False


def test_lipsync_provider(provider, video_path: Path, audio_path: Path, output_path: Path):
    """Test a lip-sync provider."""
    provider_name = provider.__class__.__name__
    logger.info(f"Testing {provider_name}...")
    
    if not provider.is_available():
        logger.warning(f"{provider_name} is not available (skipping)")
        return False
    
    if not video_path.exists():
        logger.warning(f"Test video not found: {video_path} (skipping)")
        return False
    
    if not audio_path.exists():
        logger.warning(f"Test audio not found: {audio_path} (skipping)")
        return False
    
    try:
        result = provider.apply_lipsync(video_path, audio_path, output_path)
        if result.exists():
            logger.info(f"✅ {provider_name} succeeded: {result}")
            return True
        else:
            logger.error(f"❌ {provider_name} failed: Output file not found")
            return False
    except Exception as e:
        logger.error(f"❌ {provider_name} failed: {str(e)}")
        return False


def test_video_provider(provider, script: str, avatar_id: str, output_path: Path):
    """Test a complete video provider."""
    provider_name = provider.__class__.__name__
    logger.info(f"Testing {provider_name}...")
    
    if not provider.is_available():
        logger.warning(f"{provider_name} is not available (skipping)")
        return False
    
    try:
        result = provider.generate_video(script, avatar_id, output_path)
        if result.exists():
            logger.info(f"✅ {provider_name} succeeded: {result}")
            return True
        else:
            logger.error(f"❌ {provider_name} failed: Output file not found")
            return False
    except Exception as e:
        logger.error(f"❌ {provider_name} failed: {str(e)}")
        return False


def main():
    """Run all provider tests."""
    logger.info("=" * 60)
    logger.info("Provider Testing Suite")
    logger.info("=" * 60)
    
    # Create test directory
    test_dir = Path("/tmp/grido_provider_tests")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    results = {
        "tts": {},
        "lipsync": {},
        "video": {},
    }
    
    # Test TTS Providers
    logger.info("\n" + "=" * 60)
    logger.info("Testing TTS Providers")
    logger.info("=" * 60)
    
    test_text = "Hola, este es un test de síntesis de voz."
    
    # Kokoro
    kokoro = KokoroTTSProvider()
    kokoro_output = test_dir / "kokoro_test.wav"
    results["tts"]["Kokoro"] = test_tts_provider(kokoro, test_text, kokoro_output)
    
    # ElevenLabs
    elevenlabs = ElevenLabsTTSProvider()
    elevenlabs_output = test_dir / "elevenlabs_test.wav"
    results["tts"]["ElevenLabs"] = test_tts_provider(elevenlabs, test_text, elevenlabs_output)
    
    # Test Lip-sync Providers
    logger.info("\n" + "=" * 60)
    logger.info("Testing Lip-sync Providers")
    logger.info("=" * 60)
    
    # Use a test audio file if available, or create a dummy one
    test_audio = test_dir / "test_audio.wav"
    if not test_audio.exists():
        # Create a dummy audio file using ffmpeg
        import subprocess
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
            "-t", "3", "-y", str(test_audio)
        ], capture_output=True)
    
    # Use assets if available
    test_video = Path("assets/frame3_santa_base.mp4")
    if not test_video.exists():
        logger.warning("Test video not found, skipping lip-sync tests")
    else:
        musetalk = MuseTalkLipsyncProvider()
        musetalk_output = test_dir / "musetalk_test.mp4"
        results["lipsync"]["MuseTalk"] = test_lipsync_provider(
            musetalk, test_video, test_audio, musetalk_output
        )
    
    # Test Video Providers
    logger.info("\n" + "=" * 60)
    logger.info("Testing Video Providers")
    logger.info("=" * 60)
    
    test_script = "Hola, este es un test de generación de video completo."
    heygen = HeyGenVideoProvider()
    heygen_output = test_dir / "heygen_test.mp4"
    results["video"]["HeyGen"] = test_video_provider(
        heygen, test_script, "default", heygen_output
    )
    
    # Test ProviderManager
    logger.info("\n" + "=" * 60)
    logger.info("Testing ProviderManager")
    logger.info("=" * 60)
    
    manager = ProviderManager()
    logger.info(f"TTS Providers available: {len(manager.tts_providers)}")
    logger.info(f"Lip-sync Providers available: {len(manager.lipsync_providers)}")
    logger.info(f"Video Providers available: {len(manager.video_providers)}")
    
    # Test fallback
    if manager.tts_providers:
        test_output = test_dir / "manager_tts_test.wav"
        try:
            result = manager.generate_audio_with_fallback(
                test_text, test_output, "test"
            )
            logger.info(f"✅ ProviderManager TTS fallback succeeded: {result}")
        except Exception as e:
            logger.error(f"❌ ProviderManager TTS fallback failed: {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for category, providers in results.items():
        logger.info(f"\n{category.upper()}:")
        for provider_name, success in providers.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {provider_name}: {status}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Testing complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()


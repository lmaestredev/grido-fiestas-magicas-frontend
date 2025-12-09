"""
Provider Configuration and Validation Module.

Este módulo valida todos los providers al inicio de la aplicación.
Si no hay al menos una IA disponible, la aplicación falla con un error claro.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
if str(worker_dir) not in sys.path:
    sys.path.insert(0, str(worker_dir))

# Importar providers
from providers.heygen_video import HeyGenVideoProvider
from providers.higgsfield_video import HiggsfieldVideoProvider
from providers.wav2lip_lipsync import Wav2LipLipsyncProvider
from providers.elevenlabs_tts import ElevenLabsTTSProvider

logger = logging.getLogger(__name__)


class ProviderConfig:
    """Configuración validada de providers disponibles."""
    
    def __init__(self):
        self.heygen: Optional[HeyGenVideoProvider] = None
        self.higgsfield: Optional[HiggsfieldVideoProvider] = None
        self.wav2lip: Optional[Wav2LipLipsyncProvider] = None
        self.elevenlabs: Optional[ElevenLabsTTSProvider] = None
        
        self.available_providers: List[str] = []
        self.provider_order: List[str] = []
    
    def has_any_provider(self) -> bool:
        """Verifica si hay al menos un provider disponible."""
        return len(self.available_providers) > 0
    
    def get_provider_order(self) -> List[str]:
        """Retorna el orden de prioridad de providers disponibles."""
        return self.provider_order.copy()


def validate_heygen() -> Optional[HeyGenVideoProvider]:
    """Valida y retorna HeyGen provider si está disponible."""
    if os.getenv("DISABLE_HEYGEN", "false").lower() == "true":
        logger.debug("HeyGen está deshabilitado (DISABLE_HEYGEN=true)")
        return None
    
    try:
        provider = HeyGenVideoProvider()
        if provider.is_available():
            logger.info("✅ HeyGen disponible y validado")
            return provider
        else:
            logger.warning("⚠️  HeyGen no disponible (falta HEYGEN_API_KEY)")
            return None
    except Exception as e:
        logger.warning(f"⚠️  Error validando HeyGen: {str(e)}")
        return None


def validate_higgsfield() -> Optional[HiggsfieldVideoProvider]:
    """Valida y retorna Higgsfield provider si está disponible."""
    if os.getenv("DISABLE_HIGGSFIELD", "false").lower() == "true":
        logger.debug("Higgsfield está deshabilitado (DISABLE_HIGGSFIELD=true)")
        return None
    
    try:
        provider = HiggsfieldVideoProvider()
        if provider.is_available():
            logger.info("✅ Higgsfield disponible y validado")
            return provider
        else:
            logger.warning("⚠️  Higgsfield no disponible (faltan credenciales)")
            return None
    except Exception as e:
        logger.warning(f"⚠️  Error validando Higgsfield: {str(e)}")
        return None


def validate_wav2lip() -> Optional[Wav2LipLipsyncProvider]:
    """Valida y retorna Wav2Lip provider si está disponible."""
    if os.getenv("DISABLE_WAV2LIP", "false").lower() == "true":
        logger.debug("Wav2Lip está deshabilitado (DISABLE_WAV2LIP=true)")
        return None
    
    try:
        provider = Wav2LipLipsyncProvider()
        if provider.is_available():
            logger.info("✅ Wav2Lip disponible y validado")
            return provider
        else:
            logger.warning("⚠️  Wav2Lip no disponible (falta configuración)")
            return None
    except Exception as e:
        logger.warning(f"⚠️  Error validando Wav2Lip: {str(e)}")
        return None


def validate_elevenlabs() -> Optional[ElevenLabsTTSProvider]:
    """Valida y retorna ElevenLabs provider si está disponible."""
    if os.getenv("DISABLE_ELEVENLABS", "false").lower() == "true":
        logger.debug("ElevenLabs está deshabilitado (DISABLE_ELEVENLABS=true)")
        return None
    
    try:
        provider = ElevenLabsTTSProvider()
        if provider.is_available():
            logger.info("✅ ElevenLabs disponible y validado")
            return provider
        else:
            logger.warning("⚠️  ElevenLabs no disponible (falta ELEVENLABS_API_KEY)")
            return None
    except Exception as e:
        logger.warning(f"⚠️  Error validando ElevenLabs: {str(e)}")
        return None


def validate_providers() -> ProviderConfig:
    """
    Valida todos los providers y retorna configuración validada.
    
    Orden de prioridad:
    1. HeyGen (Video completo)
    2. Higgsfield (Video completo)
    3. Wav2Lip (TTS + lip-sync)
    4. ElevenLabs (TTS + base video)
    
    Returns:
        ProviderConfig con providers validados y ordenados
        
    Raises:
        Exception: Si no hay al menos un provider disponible
    """
    logger.info("🔍 Validando providers al inicio...")
    
    config = ProviderConfig()
    
    # Validar en orden de prioridad
    config.heygen = validate_heygen()
    if config.heygen:
        config.available_providers.append("heygen")
        config.provider_order.append("heygen")
    
    config.higgsfield = validate_higgsfield()
    if config.higgsfield:
        config.available_providers.append("higgsfield")
        config.provider_order.append("higgsfield")
    
    config.wav2lip = validate_wav2lip()
    if config.wav2lip:
        config.available_providers.append("wav2lip")
        config.provider_order.append("wav2lip")
    
    config.elevenlabs = validate_elevenlabs()
    if config.elevenlabs:
        config.available_providers.append("elevenlabs")
        config.provider_order.append("elevenlabs")
    
    # Verificar que haya al menos un provider disponible
    if not config.has_any_provider():
        error_msg = (
            "❌ ERROR CRÍTICO: No hay ningún provider de IA disponible.\n"
            "   Configura al menos uno de los siguientes:\n"
            "   - HEYGEN_API_KEY (para HeyGen)\n"
            "   - HIGGSFIELD_API_KEY_ID y HIGGSFIELD_API_KEY_SECRET (para Higgsfield)\n"
            "   - WAV2LIP_MODEL_PATH y WAV2LIP_REPO_PATH (para Wav2Lip)\n"
            "   - ELEVENLABS_API_KEY (para ElevenLabs)\n"
            "\n"
            "   Revisa tu archivo .env y asegúrate de tener al menos una IA configurada."
        )
        logger.error(error_msg)
        raise Exception("No hay providers de IA disponibles. Configura al menos uno.")
    
    logger.info(
        f"✅ Validación completada: {len(config.available_providers)} provider(s) disponible(s) - "
        f"Orden: {' → '.join(config.provider_order)}"
    )
    
    return config


if __name__ == "__main__":
    """Ejecutar validación desde línea de comandos."""
    logging.basicConfig(level=logging.INFO)
    try:
        config = validate_providers()
        print(f"\n✅ Validación exitosa: {len(config.available_providers)} provider(s) disponible(s)")
        print(f"   Orden de prioridad: {' → '.join(config.provider_order)}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Validación falló: {str(e)}")
        sys.exit(1)


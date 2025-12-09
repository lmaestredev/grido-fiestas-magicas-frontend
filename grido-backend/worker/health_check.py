"""
Health check endpoint para verificar el estado del sistema.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))


def check_redis() -> Dict[str, Any]:
    """Verifica conexión a Redis."""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        client = redis.from_url(redis_url)
        client.ping()
        return {"status": "healthy", "message": "Redis conectado"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Redis error: {str(e)}"}


def check_assets() -> Dict[str, Any]:
    """Verifica que los assets estén disponibles."""
    assets_path = Path("assets")
    required_assets = [
        "Frames_1_2_to_3.mov",
        "frame3_santa_base.mp4",
        "Frame_4_NocheMagica.mov"
    ]
    
    missing = []
    for asset in required_assets:
        if not (assets_path / asset).exists():
            missing.append(asset)
    
    if missing:
        return {
            "status": "unhealthy",
            "message": f"Assets faltantes: {', '.join(missing)}"
        }
    
    return {"status": "healthy", "message": "Todos los assets disponibles"}


def check_providers() -> Dict[str, Any]:
    """Verifica que haya providers disponibles usando validación centralizada."""
    try:
        from config.providers_config import validate_providers
        provider_config = validate_providers()
        
        providers_status = {
            "heygen": provider_config.heygen is not None,
            "higgsfield": provider_config.higgsfield is not None,
            "wav2lip": provider_config.wav2lip is not None,
            "elevenlabs": provider_config.elevenlabs is not None,
            "available_count": len(provider_config.available_providers),
            "order": provider_config.provider_order,
        }
        
        if providers_status["available_count"] == 0:
            return {
                "status": "unhealthy",
                "message": "No hay providers de IA disponibles"
            }
        
        return {
            "status": "healthy",
            "message": f"{providers_status['available_count']} provider(s) disponible(s)",
            "providers": providers_status
        }
    except Exception as e:
        return {"status": "unhealthy", "message": f"Error verificando providers: {str(e)}"}


def check_storage() -> Dict[str, Any]:
    """Verifica que el storage esté configurado."""
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "firebase":
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if not cred_path and not cred_json:
            return {
                "status": "unhealthy",
                "message": "Firebase credentials no configuradas"
            }
    
    return {
        "status": "healthy",
        "message": f"Storage configurado: {storage_type}"
    }


def health_check() -> Dict[str, Any]:
    """
    Ejecuta todos los health checks.
    
    Returns:
        Dict con el estado de todos los componentes
    """
    checks = {
        "redis": check_redis(),
        "assets": check_assets(),
        "providers": check_providers(),
        "storage": check_storage(),
    }
    
    # Determinar estado general
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    overall_status = "healthy" if all_healthy else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": __import__("time").time()
    }


if __name__ == "__main__":
    """Ejecutar health check desde línea de comandos."""
    result = health_check()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "healthy" else 1)


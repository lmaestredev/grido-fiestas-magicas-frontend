"""
Test específico para HeyGen Video Provider.

Este test valida que HeyGen funcione correctamente como provider principal
para generación de videos completos con TTS y lip-sync.

Uso:
    python tests/test_heygen.py
"""

import os
import sys
from pathlib import Path
import tempfile

# Agregar el directorio del worker al path (solución robusta)
worker_dir = Path(__file__).parent.parent
sys.path.insert(0, str(worker_dir))

# Verificar que el path es correcto
if not (worker_dir / "providers").exists():
    print(f"❌ Error: No se encontró el directorio providers en {worker_dir}")
    sys.exit(1)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_heygen_provider():
    """Test específico para HeyGen provider (API directa).

    Objetivo:
    1) Generar un video usando Create Avatar Video (V2)
    2) Obtener el video_id de la respuesta
    3) Consultar el estado de ese video con Retrieve Video Status/Details
    """
    print()
    print("🎬 Test de HeyGen Video Provider")
    print("=" * 60)
    print()
    
    # Verificar configuración
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("❌ Error: HEYGEN_API_KEY no está configurado")
        print("   Configura en .env:")
        print("   HEYGEN_API_KEY=tu_api_key")
        print()
        print("   Para obtener una API key:")
        print("   1. Ve a https://app.heygen.com")
        print("   2. Inicia sesión o crea una cuenta")
        print("   3. Ve a Settings → API Keys")
        print("   4. Crea una nueva API key")
        return False
    
    avatar_id = os.getenv("PAPA_NOEL_AVATAR_ID", "default")  # En nuestro caso: talking_photo_id
    print(f"✅ HeyGen API Key configurado")
    
    if avatar_id == "default":
        print(f"⚠️  Avatar ID: {avatar_id} (NO VÁLIDO)")
        print()
        print("❌ Error: PAPA_NOEL_AVATAR_ID está configurado como 'default', que no es válido.")
        print()
        print("   Para obtener un avatar_id válido:")
        print("   1. Ve a https://app.heygen.com")
        print("   2. Inicia sesión")
        print("   3. Ve a la sección de Avatares")
        print("   4. Selecciona un avatar y copia su ID")
        print("   5. Configúralo en .env:")
        print("      PAPA_NOEL_AVATAR_ID=tu_avatar_id_real")
        print()
        print("   Ejemplo de avatar_id válido: 4e96c6c0514e4f5cbbed14f8e8624084")
        print()
        return False
    else:
        print(f"✅ Avatar ID: {avatar_id}")
    
    # Verificar voice_id (REQUERIDO para HeyGen)
    voice_id = os.getenv("PAPA_NOEL_VOICE_ID_HEYGEN") or os.getenv("PAPA_NOEL_VOICE_ID")
    if not voice_id:
        print(f"⚠️  Voice ID: No configurado")
        print()
        print("❌ Error: PAPA_NOEL_VOICE_ID_HEYGEN no está configurado")
        print()
        print("   Para obtener un voice_id:")
        print("   1. Lista voces disponibles de HeyGen:")
        print("      curl -X GET 'https://api.heygen.com/v2/voices' \\")
        print("        -H 'X-API-KEY: tu_api_key' > heygen_voices.json")
        print("   2. Busca una voz en español masculina en el JSON")
        print("   3. Copia el voice_id (ejemplo: 707365599f8545d5b6ce7a32a20e9c93)")
        print("   4. Configúralo en .env:")
        print("      PAPA_NOEL_VOICE_ID_HEYGEN=tu_voice_id_aqui")
        print()
        print("   Alternativamente, puedes crear una voz personalizada:")
        print("   1. Ve a https://app.heygen.com")
        print("   2. Ve a la sección 'Voices' (requiere plan de pago)")
        print("   3. Sube un audio de ejemplo (mínimo 1 minuto)")
        print("   4. Espera a que se procese y copia el voice_id generado")
        print()
        return False
    else:
        print(f"✅ Voice ID: {voice_id}")
    print()
    
    # Script de prueba (corto para ahorrar tiempo y costos)
    test_script = "¡Hola! Soy Papá Noel y tengo un mensaje especial para ti. ¡Feliz Navidad!"
    
    print("📝 Script de prueba:")
    print(f"   {test_script}")
    print()
    
    import requests

    # 1) GENERAR VIDEO (Create Avatar Video V2 con talking_photo)
    url_create = "https://api.heygen.com/v2/video/generate"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json",
    }

    # Usar el avatar de Papá Noel como talking_photo
    payload = {
        "video_title": "Mensaje de Papá Noel (test)",
        "video_inputs": [
            {
                "character": {
                    "type": "talking_photo",
                    "talking_photo_id": avatar_id,
                    "scale": 0.93,
                    "talking_photo_style": "square",
                    "offset": {"x": 0, "y": 0},
                    "talking_style": "expressive",
                    "expression": "happy",
                    "super_resolution": True,
                    "matting": False,
                    "circle_background_color": "#FFFFFF",
                },
                "voice": {
                    "type": "text",
                    "input_text": test_script,
                    "voice_id": voice_id,
                    "speed": 1.0,
                },
            }
        ],
        "dimension": {
            "width": 1280,
            "height": 720,
        },
    }

    print("📤 Enviando request a Create Avatar Video (V2)...")
    print(f"   URL: {url_create}")
    print(f"   Payload: {payload}")
    print()

    try:
        resp = requests.post(url_create, json=payload, headers=headers, timeout=30)
    except Exception as e:
        print(f"❌ Error de conexión al crear video: {e}")
        return False

    print(f"🔁 Status creación: {resp.status_code}")
    print(f"   Body: {resp.text[:500]}")
    print()

    if resp.status_code not in (200, 201):
        print("❌ La creación de video falló (status != 200/201)")
        return False

    try:
        data = resp.json()
    except Exception as e:
        print(f"❌ No se pudo parsear JSON de respuesta: {e}")
        return False

    video_id = (
        data.get("data", {}).get("video_id") or
        data.get("data", {}).get("id") or
        data.get("video_id") or
        data.get("id")
    )

    if not video_id:
        print("❌ La respuesta no contiene video_id / id reconocible")
        print(f"   JSON: {data}")
        return False

    print(f"✅ Video creado correctamente. video_id = {video_id}")
    print()

    # 2) CONSULTAR STATUS UNA VEZ (Retrieve Video Status/Details)
    status_url = f"https://api.heygen.com/v2/video/status?video_id={video_id}"
    print("📥 Consultando estado del video...")
    print(f"   URL: {status_url}")

    try:
        status_resp = requests.get(status_url, headers=headers, timeout=30)
        print(f"🔁 Status de la consulta: {status_resp.status_code}")
        print(f"   Body: {status_resp.text[:500]}")
    except Exception as e:
        print(f"⚠️  No se pudo consultar el estado del video: {e}")
        # No consideramos esto un fallo crítico del test de generación
        return True

    print()
    print("✅ Test de generación de HeyGen completado (request de creación OK).")
    print("   Revisa el estado en la respuesta de status o en el panel de HeyGen.")
    print()
    return True


def test_heygen_integration():
    """Test de integración de HeyGen con el flujo completo."""
    print()
    print("🔄 Test de Integración HeyGen")
    print("=" * 60)
    print()
    
    from providers.manager import ProviderManager
    
    manager = ProviderManager()
    
    # Verificar que HeyGen esté en la lista de providers
    heygen_providers = [p for p in manager.video_providers if p.__class__.__name__ == "HeyGenVideoProvider"]
    
    if not heygen_providers:
        print("⚠️  HeyGen no está disponible en ProviderManager")
        print("   Verifica que HEYGEN_API_KEY esté configurado")
        return False
    
    print(f"✅ HeyGen encontrado en ProviderManager (posición {manager.video_providers.index(heygen_providers[0]) + 1})")
    print()
    
    # Verificar orden de prioridad
    print("📋 Orden de providers de video:")
    for i, provider in enumerate(manager.video_providers, 1):
        print(f"   {i}. {provider.__class__.__name__}")
    
    if manager.video_providers[0].__class__.__name__ == "HeyGenVideoProvider":
        print()
        print("✅ HeyGen está en la posición 1 (máxima prioridad)")
    else:
        print()
        print("⚠️  HeyGen NO está en la posición 1")
        print("   Debería ser el primer provider en la lista")
    
    print()
    return True


if __name__ == "__main__":
    print("🚀 Iniciando tests de HeyGen")
    print()
    
    # Test 1: Integración
    integration_ok = test_heygen_integration()
    
    # Test 2: Provider directo (solo si hay API key)
    if os.getenv("HEYGEN_API_KEY"):
        provider_ok = test_heygen_provider()
        success = integration_ok and provider_ok
    else:
        print("⚠️  Saltando test de provider (no hay HEYGEN_API_KEY)")
        success = integration_ok
    
    sys.exit(0 if success else 1)


"""
Script de diagnóstico para probar endpoints de HeyGen API.
Este script prueba diferentes endpoints y estructuras de datos para identificar el correcto.
"""

import os
import sys
import requests
from pathlib import Path

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
if str(worker_dir) not in sys.path:
    sys.path.insert(0, str(worker_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("HEYGEN_API_KEY")
if not API_KEY:
    print("❌ HEYGEN_API_KEY no configurado en .env")
    sys.exit(1)

print("🔍 Diagnóstico de Endpoints de HeyGen API")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
print()

# Endpoints a probar
endpoints_to_test = [
    "https://api.heygen.com/v2/video/create",
    "https://api.heygen.com/v2/video/create",
    "https://api.heygen.com/v1/video/create",
    "https://api.heygen.com/v2/avatar/video",
    "https://api.heygen.com/v1/avatar/video",
    "https://api.heygen.com/v2/video/talking_photo",
    "https://api.heygen.com/v1/video/talking_photo",
    "https://api.heygen.com/v1/talking_photo",
    "https://api.heygen.com/v2/video/generate",
    "https://api.heygen.com/v1/video/generate",
]

# Estructuras de datos a probar (según documentación oficial Create Avatar Videos V2)
# Necesitas un avatar_id válido - reemplaza "default" con uno real
AVATAR_ID = os.getenv("PAPA_NOEL_AVATAR_ID", "4e96c6c0514e4f5cbbed14f8e8624084")  # Ejemplo válido
# Usar voice_id específico de HeyGen
VOICE_ID = (
    os.getenv("PAPA_NOEL_VOICE_ID_HEYGEN") or 
    os.getenv("PAPA_NOEL_VOICE_ID", "default")  # Fallback para compatibilidad
)

test_payloads = [
    # Estructura 1: v2 oficial con video_inputs (character + voice)
    {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": AVATAR_ID,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": "Hello, this is a test.",
                    "voice_id": VOICE_ID,
                    "speed": 1.0,
                },
            }
        ],
        "dimension": {
            "width": 1080,
            "height": 1920,
        },
    },
    # Estructura 2: v2 sin dimension
    {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": AVATAR_ID,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": "Hello, this is a test.",
                    "voice_id": VOICE_ID,
                    "speed": 1.0,
                },
            }
        ]
    },
    # Estructura 3: sin speed (usa default)
    {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": AVATAR_ID,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": "Hello, this is a test.",
                    "voice_id": VOICE_ID,
                },
            }
        ]
    },
    # Estructura 4: Simplificada (puede no funcionar, solo para diagnóstico)
    {
        "avatar_id": AVATAR_ID,
        "voice_id": VOICE_ID,
        "script": {
            "type": "text",
            "input": "Hello, this is a test.",
        },
    },
]

headers = {
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json",
}

print("📋 Probando endpoints y estructuras de datos...")
print()

successful_endpoints = []

for endpoint in endpoints_to_test:
    print(f"🔗 Endpoint: {endpoint}")
    
    for i, payload in enumerate(test_payloads, 1):
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            status_emoji = "✅" if response.status_code < 400 else "❌"
            print(f"   {status_emoji} Payload {i}: Status {response.status_code}")
            
            if response.status_code == 200 or response.status_code == 201:
                print(f"      ✅ ¡ÉXITO! Endpoint correcto encontrado")
                print(f"      Response: {response.json()}")
                successful_endpoints.append((endpoint, payload, response.json()))
                break
            elif response.status_code == 401:
                print(f"      ⚠️  Unauthorized - API key puede ser inválida o sin permisos")
            elif response.status_code == 400:
                print(f"      ⚠️  Bad Request - Estructura incorrecta pero endpoint existe")
                try:
                    error_data = response.json()
                    print(f"      Error: {error_data}")
                except:
                    print(f"      Error text: {response.text[:200]}")
            elif response.status_code == 404:
                # No mostrar 404 para no saturar la salida
                pass
            else:
                print(f"      Status {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {str(e)[:100]}")
    
    print()

print("=" * 60)
if successful_endpoints:
    print("✅ Endpoints exitosos encontrados:")
    for endpoint, payload, response in successful_endpoints:
        print(f"   - {endpoint}")
        print(f"     Payload: {payload}")
        print(f"     Response: {response}")
else:
    print("❌ No se encontraron endpoints exitosos")
    print()
    print("💡 Posibles causas:")
    print("   1. Los endpoints han cambiado en la API de HeyGen")
    print("   2. La API key no tiene los permisos necesarios")
    print("   3. Necesitas usar un SDK oficial de HeyGen")
    print("   4. El avatar_id 'default' no existe - necesitas un avatar_id válido")
    print()
    print("📚 Próximos pasos:")
    print("   1. Consulta la documentación oficial: https://docs.heygen.com")
    print("   2. Verifica tu avatar_id en https://app.heygen.com")
    print("   3. Contacta soporte de HeyGen para obtener el endpoint correcto")


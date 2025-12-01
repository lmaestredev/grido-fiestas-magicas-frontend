"""
Script para probar HeyGen con las credenciales proporcionadas.
"""

import os
import sys
import requests
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Key proporcionada
HEYGEN_API_KEY = "sk_V2_hgu_koq8ujUoICY_UEcuw6TNrwEkkoOwYCtoMsnZtJbHuZCZ"

def test_heygen_endpoints():
    """Prueba diferentes endpoints de HeyGen."""
    print("=" * 60)
    print("🔍 Probando HeyGen API")
    print("=" * 60)
    print()
    
    headers = {
        "X-API-KEY": HEYGEN_API_KEY,
        "Content-Type": "application/json",
    }
    
    # Endpoints a probar
    endpoints = [
        "https://api.heygen.com/v2/avatar/video",
        "https://api.heygen.com/v2/video.generate",
        "https://api.heygen.com/v1/video/talking_photo",
        "https://api.heygen.com/v1/talking_photo",
        "https://api.heygen.com/v1/video.generate",
    ]
    
    # Datos de prueba simples
    test_data = {
        "avatar_id": "default",
        "text": "Hello, this is a test",
    }
    
    for endpoint in endpoints:
        print(f"📡 Probando: {endpoint}")
        try:
            response = requests.post(
                endpoint,
                json=test_data,
                headers=headers,
                timeout=10
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200 or response.status_code == 201:
                print(f"   ✅ ÉXITO!")
                print(f"   Response: {response.json()}")
                return endpoint, response.json()
            else:
                print(f"   ❌ Error: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)[:200]}")
        print()
    
    # También probar GET para verificar autenticación
    print("📡 Probando autenticación con GET...")
    try:
        # Intentar obtener información de la cuenta
        response = requests.get(
            "https://api.heygen.com/v1/user",
            headers=headers,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Autenticación válida!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)[:200]}")
    
    return None, None


if __name__ == "__main__":
    endpoint, result = test_heygen_endpoints()
    if endpoint:
        print()
        print("=" * 60)
        print(f"✅ Endpoint funcional encontrado: {endpoint}")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ No se encontró ningún endpoint funcional")
        print("=" * 60)


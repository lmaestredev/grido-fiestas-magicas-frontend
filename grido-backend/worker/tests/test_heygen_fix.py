"""
Script para diagnosticar y corregir problemas con HeyGen API.
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

HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY", "sk_V2_hgu_koq8ujUoICY_UEcuw6TNrwEkkoOwYCtoMsnZtJbHuZCZ")

def test_heygen_authentication():
    """Prueba diferentes métodos de autenticación."""
    print("=" * 60)
    print("🔍 Diagnóstico HeyGen API")
    print("=" * 60)
    print()
    
    # Métodos de autenticación a probar
    auth_methods = [
        ("X-API-KEY", HEYGEN_API_KEY),
        ("Authorization", f"Bearer {HEYGEN_API_KEY}"),
        ("Authorization", f"ApiKey {HEYGEN_API_KEY}"),
        ("X-Api-Key", HEYGEN_API_KEY),
        ("api-key", HEYGEN_API_KEY),
    ]
    
    # Endpoints base a probar
    base_urls = [
        "https://api.heygen.com",
        "https://api.heygen.com/v1",
        "https://api.heygen.com/v2",
        "https://api.heygen.com/v3",
    ]
    
    # Endpoints específicos
    endpoints = [
        "/user",
        "/user/info",
        "/account",
        "/avatar/list",
        "/avatar",
        "/video/generate",
        "/video/talking_photo",
        "/talking_photo",
    ]
    
    for auth_header, auth_value in auth_methods:
        print(f"📡 Probando autenticación: {auth_header}")
        print("-" * 60)
        
        for base_url in base_urls:
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                headers = {
                    auth_header: auth_value,
                    "Content-Type": "application/json",
                }
                
                try:
                    # Probar GET primero
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code != 404:
                        print(f"   ✅ GET {url}: {response.status_code}")
                        if response.status_code == 200:
                            print(f"      Response: {response.json()}")
                            return url, headers, "GET"
                    
                    # Probar POST con datos mínimos
                    test_data = {"test": "data"}
                    response = requests.post(url, json=test_data, headers=headers, timeout=10)
                    if response.status_code != 404:
                        print(f"   ✅ POST {url}: {response.status_code}")
                        if response.status_code == 200 or response.status_code == 201:
                            print(f"      Response: {response.json()}")
                            return url, headers, "POST"
                
                except requests.exceptions.RequestException as e:
                    pass
        
        print()
    
    return None, None, None


def check_heygen_documentation():
    """Sugiere revisar documentación actualizada."""
    print("=" * 60)
    print("📚 Recomendaciones para HeyGen")
    print("=" * 60)
    print()
    print("1. Verificar en el dashboard de HeyGen:")
    print("   - https://app.heygen.com/login")
    print("   - Ir a Settings > API")
    print("   - Verificar que la API key sea válida")
    print()
    print("2. Revisar documentación actualizada:")
    print("   - https://docs.heygen.com")
    print("   - Buscar 'Create Avatar Videos' o 'API Reference'")
    print()
    print("3. Verificar versión de la API:")
    print("   - Puede que hayan cambiado a v3")
    print("   - O que requieran autenticación diferente")
    print()
    print("4. Contactar soporte si es necesario:")
    print("   - support@heygen.com")
    print()


if __name__ == "__main__":
    url, headers, method = test_heygen_authentication()
    
    if url:
        print()
        print("=" * 60)
        print(f"✅ Endpoint funcional encontrado!")
        print("=" * 60)
        print(f"URL: {url}")
        print(f"Method: {method}")
        print(f"Headers: {headers}")
    else:
        print()
        print("=" * 60)
        print("❌ No se encontró ningún endpoint funcional")
        print("=" * 60)
        check_heygen_documentation()


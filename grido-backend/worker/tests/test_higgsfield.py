"""
Script para probar Higgsfield API con las credenciales proporcionadas.
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

# Credenciales proporcionadas
HIGGSFIELD_API_KEY_ID = "a242bf13-bfe5-4aa4-af63-245d05d48d22"
HIGGSFIELD_API_KEY_SECRET = "19b359462d24010924f52a74048d9ab190f2d0336f48a758bd0f1ccc242b4b1a"

def test_higgsfield_authentication():
    """Prueba diferentes métodos de autenticación con Higgsfield."""
    print("=" * 60)
    print("🔍 Probando Higgsfield API")
    print("=" * 60)
    print()
    print(f"API Key ID: {HIGGSFIELD_API_KEY_ID[:20]}...")
    print(f"API Key Secret: {HIGGSFIELD_API_KEY_SECRET[:20]}...")
    print()
    
    # Métodos de autenticación a probar
    auth_methods = [
        {
            "name": "Bearer ID + X-API-Key Secret",
            "headers": {
                "Authorization": f"Bearer {HIGGSFIELD_API_KEY_ID}",
                "X-API-Key": HIGGSFIELD_API_KEY_SECRET,
                "Content-Type": "application/json",
            }
        },
        {
            "name": "Bearer Secret + X-API-Key ID",
            "headers": {
                "Authorization": f"Bearer {HIGGSFIELD_API_KEY_SECRET}",
                "X-API-Key": HIGGSFIELD_API_KEY_ID,
                "Content-Type": "application/json",
            }
        },
        {
            "name": "X-API-Key-ID + X-API-Key-Secret",
            "headers": {
                "X-API-Key-ID": HIGGSFIELD_API_KEY_ID,
                "X-API-Key-Secret": HIGGSFIELD_API_KEY_SECRET,
                "Content-Type": "application/json",
            }
        },
        {
            "name": "Bearer ID only",
            "headers": {
                "Authorization": f"Bearer {HIGGSFIELD_API_KEY_ID}",
                "Content-Type": "application/json",
            }
        },
    ]
    
    # Endpoints base a probar
    base_urls = [
        "https://cloud.higgsfield.ai/api",
        "https://cloud.higgsfield.ai/api/v1",
        "https://api.higgsfield.ai",
        "https://api.higgsfield.ai/v1",
    ]
    
    # Endpoints específicos
    endpoints = [
        "/user",
        "/account",
        "/generate",
        "/video/generate",
        "/status",
    ]
    
    for auth_method in auth_methods:
        print(f"📡 Probando: {auth_method['name']}")
        print("-" * 60)
        
        for base_url in base_urls:
            for endpoint in endpoints:
                url = f"{base_url}{endpoint}"
                
                try:
                    # Probar GET primero
                    response = requests.get(url, headers=auth_method["headers"], timeout=10)
                    if response.status_code not in [404, 405]:
                        print(f"   ✅ GET {url}: {response.status_code}")
                        if response.status_code == 200:
                            try:
                                print(f"      Response: {response.json()}")
                            except:
                                print(f"      Response: {response.text[:200]}")
                            return url, auth_method["headers"], "GET"
                    
                    # Probar POST con datos mínimos
                    test_data = {"test": "data"}
                    response = requests.post(url, json=test_data, headers=auth_method["headers"], timeout=10)
                    if response.status_code not in [404, 405]:
                        print(f"   ✅ POST {url}: {response.status_code}")
                        if response.status_code in [200, 201]:
                            try:
                                print(f"      Response: {response.json()}")
                            except:
                                print(f"      Response: {response.text[:200]}")
                            return url, auth_method["headers"], "POST"
                
                except requests.exceptions.RequestException as e:
                    pass
        
        print()
    
    return None, None, None


def test_higgsfield_provider():
    """Prueba el provider de Higgsfield directamente."""
    print("=" * 60)
    print("🧪 Probando HiggsfieldVideoProvider")
    print("=" * 60)
    print()
    
    # Configurar variables de entorno temporalmente
    os.environ["HIGGSFIELD_API_KEY_ID"] = HIGGSFIELD_API_KEY_ID
    os.environ["HIGGSFIELD_API_KEY_SECRET"] = HIGGSFIELD_API_KEY_SECRET
    
    try:
        from providers.higgsfield_video import HiggsfieldVideoProvider
        
        provider = HiggsfieldVideoProvider()
        
        if provider.is_available():
            print("✅ Provider está disponible")
            print(f"   API Key ID: {provider.api_key_id[:20]}...")
            print(f"   API Key Secret: {provider.api_key_secret[:20]}...")
            print(f"   Base URL: {provider.api_base_url}")
        else:
            print("❌ Provider no está disponible")
            print(f"   API Key ID: {provider.api_key_id}")
            print(f"   API Key Secret: {provider.api_key_secret}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    url, headers, method = test_higgsfield_authentication()
    
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
    
    print()
    test_higgsfield_provider()


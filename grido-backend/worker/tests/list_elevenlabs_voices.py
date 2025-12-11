"""
Script para listar los voices disponibles en ElevenLabs.

Este script ayuda a encontrar un voice_id válido para usar en la configuración.

Uso:
    python tests/list_elevenlabs_voices.py
"""

import os
import sys
import requests
from pathlib import Path

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
sys.path.insert(0, str(worker_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def list_elevenlabs_voices():
    """Lista todos los voices disponibles en ElevenLabs."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ Error: ELEVENLABS_API_KEY no está configurado en .env")
        print("   Agrega: ELEVENLABS_API_KEY=tu_api_key")
        return False
    
    print("🔍 Listando voices disponibles en ElevenLabs...")
    print("=" * 60)
    print()
    
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key,
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        voices = data.get("voices", [])
        
        if not voices:
            print("⚠️  No se encontraron voices disponibles")
            return False
        
        print(f"✅ Se encontraron {len(voices)} voices disponibles:\n")
        
        # Buscar voces masculinas o que puedan servir para Papá Noel
        male_voices = []
        other_voices = []
        
        for voice in voices:
            voice_info = {
                "id": voice.get("voice_id"),
                "name": voice.get("name", "Sin nombre"),
                "category": voice.get("category", "unknown"),
                "description": voice.get("description", ""),
            }
            
            # Filtrar por categoría o descripción
            name_lower = voice_info["name"].lower()
            desc_lower = voice_info["description"].lower()
            
            if any(word in name_lower or word in desc_lower for word in ["male", "man", "masculine", "deep", "low", "santa", "noel"]):
                male_voices.append(voice_info)
            else:
                other_voices.append(voice_info)
        
        # Mostrar voces masculinas primero (recomendadas para Papá Noel)
        if male_voices:
            print("🎅 Voces recomendadas para Papá Noel (masculinas):")
            print("-" * 60)
            for voice in male_voices:
                print(f"  ID: {voice['id']}")
                print(f"  Nombre: {voice['name']}")
                print(f"  Categoría: {voice['category']}")
                if voice['description']:
                    print(f"  Descripción: {voice['description'][:100]}")
                print()
        
        # Mostrar otras voces
        if other_voices:
            print("📋 Otras voces disponibles:")
            print("-" * 60)
            for voice in other_voices[:10]:  # Mostrar solo las primeras 10
                print(f"  ID: {voice['id']}")
                print(f"  Nombre: {voice['name']}")
                print(f"  Categoría: {voice['category']}")
                print()
            
            if len(other_voices) > 10:
                print(f"  ... y {len(other_voices) - 10} voces más")
                print()
        
        # Sugerir un voice_id
        if male_voices:
            suggested = male_voices[0]
            print("=" * 60)
            print("💡 Voice ID sugerido para Papá Noel:")
            print(f"   PAPA_NOEL_VOICE_ID={suggested['id']}")
            print(f"   Nombre: {suggested['name']}")
            print()
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con ElevenLabs API: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Status: {e.response.status_code}")
            print(f"   Response: {e.response.text[:200]}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = list_elevenlabs_voices()
    sys.exit(0 if success else 1)


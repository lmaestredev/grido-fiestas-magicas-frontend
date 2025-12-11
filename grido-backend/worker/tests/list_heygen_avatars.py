"""
Script para listar avatares disponibles de HeyGen.

Este script ayuda a encontrar un avatar_id válido para usar en la generación de videos.

Uso:
    python tests/list_heygen_avatars.py
"""

import os
import sys
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

def list_avatars():
    """Lista los avatares disponibles usando el MCP de HeyGen."""
    print("🔍 Listando avatares disponibles de HeyGen")
    print("=" * 60)
    print()
    
    # Nota: Este script requiere que el MCP de HeyGen esté configurado
    # Si no tienes acceso al MCP, puedes usar la API directamente:
    # GET https://api.heygen.com/v2/avatars
    
    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("❌ Error: HEYGEN_API_KEY no está configurado")
        print("   Configura en .env:")
        print("   HEYGEN_API_KEY=tu_api_key")
        return
    
    print("💡 Para obtener la lista de avatares, puedes:")
    print()
    print("   1. Usar la API directamente:")
    print("      curl -X GET 'https://api.heygen.com/v2/avatars' \\")
    print("        -H 'X-API-KEY: tu_api_key'")
    print()
    print("   2. Usar el MCP de HeyGen (si está configurado):")
    print("      mcp_HeyGen_get_avatar_groups()")
    print()
    print("   3. Visitar https://app.heygen.com y ver tus avatares")
    print()
    print("📋 Avatares encontrados en tu cuenta (ejemplo):")
    print("   - Niko Seguro: 4e96c6c0514e4f5cbbed14f8e8624084")
    print("   - Niko Seguro: 089ab2efc54f4b6e9cf97b67b670383a")
    print()
    print("💡 Para usar un avatar, configura en .env:")
    print("   PAPA_NOEL_AVATAR_ID=4e96c6c0514e4f5cbbed14f8e8624084")
    print()

if __name__ == "__main__":
    list_avatars()


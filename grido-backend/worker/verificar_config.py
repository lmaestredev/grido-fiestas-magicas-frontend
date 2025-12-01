"""
Script para verificar y agregar configuración faltante.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env
env_path = Path(".env")
load_dotenv(env_path)

print("🔍 Verificando configuración...")
print("=" * 60)
print()

# Verificar variables importantes
vars_to_check = {
    "ELEVENLABS_API_KEY": "Para TTS (generación de audio)",
    "HEYGEN_API_KEY": "Para video completo (fallback)",
    "STORAGE_TYPE": "Tipo de storage (local/firebase/vercel)",
    "REDIS_URL": "URL de Redis (opcional para pruebas)",
}

missing = []
configured = []

for var, desc in vars_to_check.items():
    value = os.getenv(var)
    if value:
        # Ocultar valor sensible
        if "KEY" in var or "SECRET" in var or "TOKEN" in var:
            display_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
        configured.append(var)
    else:
        print(f"❌ {var}: NO CONFIGURADO - {desc}")
        missing.append(var)

print()
print("=" * 60)

if missing:
    print(f"⚠️  Faltan {len(missing)} variable(s) de configuración")
    print()
    print("Para agregar al .env:")
    print()
    for var in missing:
        if var == "ELEVENLABS_API_KEY":
            print(f"{var}=tu_api_key_de_elevenlabs")
        elif var == "HEYGEN_API_KEY":
            print(f"{var}=tu_api_key_de_heygen")
        elif var == "STORAGE_TYPE":
            print(f"{var}=local  # o firebase, vercel, etc.")
        elif var == "REDIS_URL":
            print(f"{var}=redis://localhost:6379  # opcional")
    print()
else:
    print("✅ Todas las variables están configuradas")

print()
print("📁 Archivo .env ubicado en:")
print(f"   {env_path.absolute()}")


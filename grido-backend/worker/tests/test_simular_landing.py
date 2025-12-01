"""
Script simplificado que simula el envío desde la landing.

Este script solo encola el trabajo en Redis, luego debes ejecutar
el worker manualmente para procesarlo.

Uso:
    # Terminal 1: Encolar trabajo
    python test_simular_landing.py
    
    # Terminal 2: Procesar (en otra terminal)
    python video-worker.py
"""

import os
import sys
import json
import time
from pathlib import Path

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def simular_envio_landing():
    """Simula el envío del formulario desde la landing."""
    print()
    print("📝 Simulando Envío desde Landing")
    print("=" * 60)
    print()
    
    # Datos del formulario
    form_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos"
    }
    
    print("📋 Datos del formulario:")
    for key, value in form_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Conectar a Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"🔗 Conectando a Redis: {redis_url}")
    
    try:
        import redis
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("   ✅ Conexión exitosa")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        print("💡 Inicia Redis:")
        print("   brew services start redis  # macOS")
        print("   O configura REDIS_URL en .env")
        return False
    
    print()
    
    # Generar video ID
    import random
    import string
    video_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    print(f"🆔 Video ID: {video_id}")
    print()
    
    # Crear job (como lo hace /api/generate-video)
    job = {
        "videoId": video_id,
        "status": "pending",
        "data": form_data,
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    # Guardar en Redis
    redis_client.set(f"job:{video_id}", json.dumps(job))
    redis_client.lpush("video:queue", video_id)
    
    print("✅ Trabajo encolado en Redis")
    print()
    print("📌 Próximo paso:")
    print("   Ejecuta el worker en otra terminal:")
    print("   cd grido-backend/worker")
    print("   source venv/bin/activate")
    print("   python3 video-worker.py")
    print()
    print(f"   El worker procesará el video: {video_id}")
    
    return True


if __name__ == "__main__":
    success = simular_envio_landing()
    sys.exit(0 if success else 1)


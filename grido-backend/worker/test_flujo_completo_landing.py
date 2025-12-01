"""
Script de prueba que simula el flujo completo desde la landing.

Este script:
1. Simula el envío del formulario (como lo haría la landing)
2. Encola el trabajo en Redis
3. Procesa el video con el worker
4. Verifica el resultado

Uso:
    python test_flujo_completo_landing.py
"""

import os
import sys
import json
import time
from pathlib import Path

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_flujo_completo():
    """Prueba el flujo completo simulando la landing."""
    print()
    print("🚀 Prueba Flujo Completo - Desde Landing")
    print("=" * 60)
    print()
    
    # Datos simulados del formulario (como los envía la landing)
    form_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos"
    }
    
    print("📝 Datos del formulario (simulando landing):")
    for key, value in form_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Verificar Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    print(f"🔗 Conectando a Redis: {redis_url}")
    
    try:
        import redis
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("   ✅ Conexión a Redis exitosa")
    except Exception as e:
        print(f"   ❌ Error conectando a Redis: {e}")
        print()
        print("💡 Opciones:")
        print("   1. Instalar Redis localmente: brew install redis (macOS)")
        print("   2. Usar Upstash Redis (producción)")
        print("   3. Configurar REDIS_URL en .env")
        return False
    
    print()
    
    # Generar video ID (como lo hace la API)
    try:
        from nanoid import generate
        video_id = generate(size=12)
    except ImportError:
        import random
        import string
        video_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    print(f"🆔 Video ID generado: {video_id}")
    print()
    
    # Paso 1: Crear job en Redis (como lo hace /api/generate-video)
    print("📤 Paso 1: Encolando trabajo en Redis...")
    try:
        job = {
            "videoId": video_id,
            "status": "pending",
            "data": form_data,
            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
        # Guardar job en Redis
        redis_client.set(f"job:{video_id}", json.dumps(job))
        
        # Agregar a la cola
        redis_client.lpush("video:queue", video_id)
        
        print(f"   ✅ Trabajo encolado: {video_id}")
    except Exception as e:
        print(f"   ❌ Error encolando trabajo: {e}")
        return False
    
    print()
    
    # Paso 2: Procesar con el worker (simulando lo que haría el worker)
    print("🎬 Paso 2: Procesando video con worker...")
    print("   (Esto puede tardar varios minutos)")
    print()
    
    try:
        # Importar función de procesamiento
        from video_worker import process_video
        
        # Procesar video
        process_video(video_id, form_data)
        
        print()
        print("   ✅ Video procesado exitosamente")
    except Exception as e:
        print(f"   ❌ Error procesando video: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Paso 3: Verificar resultado
    print("🔍 Paso 3: Verificando resultado...")
    try:
        job_data = redis_client.get(f"job:{video_id}")
        if job_data:
            job = json.loads(job_data)
            status = job.get("status")
            video_url = job.get("videoUrl")
            
            print(f"   Estado: {status}")
            if video_url:
                print(f"   URL: {video_url}")
            
            if status == "completed":
                print()
                print("=" * 60)
                print("✅ Flujo completo exitoso!")
                print()
                print("📊 Resumen:")
                print(f"   - Video ID: {video_id}")
                print(f"   - Estado: {status}")
                print(f"   - URL: {video_url}")
                return True
            else:
                print(f"   ⚠️  Estado: {status} (esperado: completed)")
                return False
        else:
            print("   ❌ Job no encontrado en Redis")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando resultado: {e}")
        return False


if __name__ == "__main__":
    success = test_flujo_completo()
    sys.exit(0 if success else 1)


"""
Script de prueba END-TO-END completo desde la landing.

Este script simula:
1. Envío del formulario desde la landing
2. Encolado del trabajo en Redis
3. Procesamiento del video por el worker
4. Generación del video completo
5. Subida a storage
6. Verificación del resultado

Uso:
    # Terminal 1: Encolar trabajo
    python test_flujo_completo_landing.py --enqueue
    
    # Terminal 2: Procesar (en otra terminal)
    python video-worker.py
    
    # O ejecutar todo en una sola vez (sin Redis)
    python test_flujo_completo_landing.py --direct
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def simular_formulario_landing():
    """Simula los datos que vienen del formulario de la landing."""
    return {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días con mucha alegría",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios, fue un día inolvidable",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos en la plaza"
    }


def encolar_trabajo_redis(form_data):
    """Encola el trabajo en Redis (como lo hace la landing)."""
    print()
    print("=" * 60)
    print("📝 PASO 1: Simulando Envío desde Landing")
    print("=" * 60)
    print()
    
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
        return None
    
    print()
    
    # Generar video ID (como lo hace la API)
    import random
    import string
    video_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    print(f"🆔 Video ID generado: {video_id}")
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
    print(f"📌 Video ID: {video_id}")
    print(f"📌 Estado: pending")
    print()
    
    return video_id


def procesar_directo(form_data):
    """Procesa el video directamente sin Redis (para pruebas rápidas)."""
    print()
    print("=" * 60)
    print("🚀 PRUEBA DIRECTA - Sin Redis")
    print("=" * 60)
    print()
    
    from providers.manager import ProviderManager
    from storage import upload_video
    
    # Generar video ID
    video_id = f"test_landing_{int(time.time())}"
    
    print(f"🆔 Video ID: {video_id}")
    print("📋 Datos del formulario:")
    for key, value in form_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Verificar assets
    assets_path = Path("assets")
    intro_video = assets_path / "Frames_1_2_to_3.mov"
    frame3_base = assets_path / "frame3_santa_base.mp4"
    outro_video = assets_path / "Frame_4_NocheMagica.mov"
    
    if not all([intro_video.exists(), frame3_base.exists(), outro_video.exists()]):
        print("❌ Error: Faltan assets")
        missing = [p.name for p in [intro_video, frame3_base, outro_video] if not p.exists()]
        print(f"   Faltan: {', '.join(missing)}")
        return False
    
    print("✅ Todos los assets encontrados")
    print()
    
    # Templates
    FRAME2_PHRASE = "¡Ho, ho, ho! Mirá lo que tengo para vos..."
    FRAME3_TEMPLATE = """
¡Hola {nombre}! Soy Papá Noel y vengo desde el Polo Norte para saludarte en esta Noche Mágica.

Tu {parentesco} me contó que este año {queHizo}. ¡Qué orgullo me da saber eso!

{recuerdoEspecial}

Y me dijeron que tu pedido especial para esta Noche Mágica es: {pedidoNocheMagica}. 
Voy a hacer todo lo posible para que se cumpla.

Desde Grido y desde el Polo Norte, te deseamos unas Fiestas Mágicas llenas de alegría. 
Y recordá, la magia está en compartir... ¡y en un rico helado de Grido!

¡Ho, ho, ho! ¡Feliz Noche Mágica desde {provincia}!
""".strip()
    
    script_frame2 = FRAME2_PHRASE
    script_frame3 = FRAME3_TEMPLATE.format(**form_data)
    
    # Crear directorio temporal
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    output_path = temp_dir / f"{video_id}.mp4"
    
    try:
        print("🎬 Generando video completo...")
        print()
        
        manager = ProviderManager()
        
        result = manager.process_video_with_fallback(
            intro_video=intro_video,
            base_video=frame3_base,
            outro_video=outro_video,
            script_frame2=script_frame2,
            script_frame3=script_frame3,
            output_path=output_path,
            video_id=video_id,
        )
        
        if not result.exists():
            print("❌ Error: Video no generado")
            return False
        
        size_mb = result.stat().st_size / (1024 * 1024)
        print(f"   ✅ Video generado: {size_mb:.2f} MB")
        print(f"   📁 Ubicación temporal: {result}")
        print()
        
        print("📤 Subiendo a storage...")
        video_url = upload_video(video_id, result)
        print(f"   ✅ Video subido")
        print(f"   🔗 URL: {video_url}")
        print()
        
        # Verificar archivo local si es storage local
        if video_url.startswith("file://"):
            local_path = video_url.replace("file://", "")
            if Path(local_path).exists():
                final_size = Path(local_path).stat().st_size / (1024 * 1024)
                print(f"   📊 Tamaño final: {final_size:.2f} MB")
                print()
                print("💡 Para reproducir:")
                print(f"   open {local_path}")
        
        print("=" * 60)
        print("✅ PRUEBA COMPLETA EXITOSA")
        print("=" * 60)
        print()
        print("📊 Resumen:")
        print(f"   - Video ID: {video_id}")
        print(f"   - Tamaño: {size_mb:.2f} MB")
        print(f"   - URL: {video_url}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Prueba flujo completo desde landing")
    parser.add_argument(
        "--enqueue",
        action="store_true",
        help="Solo encolar trabajo en Redis (luego ejecutar worker manualmente)"
    )
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Procesar directamente sin Redis (prueba rápida)"
    )
    
    args = parser.parse_args()
    
    form_data = simular_formulario_landing()
    
    if args.direct:
        # Procesar directamente
        success = procesar_directo(form_data)
        sys.exit(0 if success else 1)
    elif args.enqueue:
        # Solo encolar
        video_id = encolar_trabajo_redis(form_data)
        if video_id:
            print("📌 Próximo paso:")
            print("   Ejecuta el worker en otra terminal:")
            print("   cd grido-backend/worker")
            print("   source venv/bin/activate")
            print("   STORAGE_TYPE=local python3 video-worker.py")
            print()
            print(f"   El worker procesará el video: {video_id}")
        sys.exit(0 if video_id else 1)
    else:
        # Por defecto: procesar directamente
        print("💡 Usando modo directo (sin Redis)")
        print("   Usa --enqueue para encolar en Redis")
        print("   Usa --direct para procesar directamente")
        print()
        success = procesar_directo(form_data)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

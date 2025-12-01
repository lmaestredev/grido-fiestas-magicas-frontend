"""
Script de prueba END-TO-END completo.

Este script prueba el flujo completo:
1. Datos del formulario
2. Generación de audio con voz de Papá Noel
3. Composición de video
4. Upload a Firebase Storage
5. Obtener URL pública

Uso:
    python test_end_to_end.py
"""

import os
import sys
from pathlib import Path
import tempfile

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_end_to_end():
    """Prueba el flujo completo end-to-end."""
    print()
    print("🚀 Prueba End-to-End Completa")
    print("=" * 60)
    print()
    
    # Datos simulados del formulario
    test_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos"
    }
    
    video_id = f"test_e2e_{int(__import__('time').time())}"
    
    print(f"📝 Video ID: {video_id}")
    print("📋 Datos del formulario:")
    for key, value in test_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Verificar videos base
    assets_path = Path("assets")
    intro_video = assets_path / "Frames_1_2_to_3.mov"
    outro_video = assets_path / "Frame_4_NocheMagica.mov"
    frame3_base = assets_path / "frame3_santa_base.mp4"
    
    if not intro_video.exists():
        print(f"❌ Error: No se encuentra {intro_video}")
        return False
    
    if not outro_video.exists():
        print(f"❌ Error: No se encuentra {outro_video}")
        return False
    
    print("✅ Videos base encontrados")
    print()
    
    # Verificar providers
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    if len(manager.video_providers) == 0 and len(manager.tts_providers) == 0:
        print("❌ Error: No hay providers disponibles")
        return False
    
    print(f"✅ Providers disponibles:")
    print(f"   - TTS: {len(manager.tts_providers)}")
    for provider in manager.tts_providers:
        print(f"     * {provider.__class__.__name__}")
        if hasattr(provider, 'voice_id'):
            print(f"       Voz: {provider.voice_id}")
    print(f"   - Video: {len(manager.video_providers)}")
    for provider in manager.video_providers:
        print(f"     * {provider.__class__.__name__}")
    print()
    
    # Verificar storage
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    print(f"📦 Storage configurado: {storage_type}")
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
    script_frame3 = FRAME3_TEMPLATE.format(**test_data)
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    output_path = temp_dir / "video_final.mp4"
    
    try:
        # Paso 1: Generar video
        print("🎬 Paso 1: Generando video...")
        manager.process_video_with_fallback(
            intro_video=intro_video,
            base_video=frame3_base if frame3_base.exists() else intro_video,
            outro_video=outro_video,
            script_frame2=script_frame2,
            script_frame3=script_frame3,
            output_path=output_path,
            video_id=video_id,
        )
        
        if not output_path.exists():
            print("❌ Error: El video no se generó")
            return False
        
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ Video generado: {file_size:.2f} MB")
        print()
        
        # Paso 2: Subir a storage
        print(f"📤 Paso 2: Subiendo a {storage_type}...")
        from storage import upload_video
        video_url = upload_video(video_id, output_path)
        print(f"   ✅ Video subido")
        print(f"   🔗 URL: {video_url}")
        print()
        
        # Paso 3: Verificar URL (si es HTTP/HTTPS)
        if video_url.startswith("http"):
            print("🔍 Paso 3: Verificando URL...")
            import requests
            try:
                response = requests.head(video_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"   ✅ URL accesible (Status: {response.status_code})")
                else:
                    print(f"   ⚠️  URL responde con status: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  No se pudo verificar URL: {e}")
        else:
            print("ℹ️  Paso 3: URL local (file://) - no se puede verificar remotamente")
            local_path = video_url.replace("file://", "")
            if Path(local_path).exists():
                print(f"   ✅ Archivo existe localmente: {local_path}")
        
        print()
        print("=" * 60)
        print("✅ Prueba End-to-End completada exitosamente!")
        print()
        print("📊 Resumen:")
        print(f"   - Video ID: {video_id}")
        print(f"   - Tamaño: {file_size:.2f} MB")
        print(f"   - URL: {video_url}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_end_to_end()
    sys.exit(0 if success else 1)


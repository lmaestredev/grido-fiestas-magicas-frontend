"""
Script de prueba local para el worker de generación de video.

Este script permite probar el flujo completo localmente sin necesidad de:
- Modal
- Redis (usa mock)
- Storage remoto (usa local)

Uso:
    python test_local.py
"""

import os
import sys
from pathlib import Path
import json
from typing import Dict, Any

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv no está instalado, usar variables de entorno del sistema

# Configurar variables de entorno para prueba local (solo si no están configuradas)
os.environ.setdefault("STORAGE_TYPE", "local")
os.environ.setdefault("LOCAL_STORAGE_PATH", "./storage")

# Mock de Redis para pruebas locales
class MockRedis:
    def __init__(self):
        self.data = {}
    
    def set(self, key: str, value: str):
        self.data[key] = value
    
    def get(self, key: str):
        return self.data.get(key)
    
    def lpush(self, key: str, value: str):
        if key not in self.data:
            self.data[key] = []
        self.data[key].insert(0, value)
    
    def brpop(self, key: str, timeout: int = 0):
        if key in self.data and self.data[key]:
            value = self.data[key].pop(0)
            return (key.encode(), value.encode())
        return None
    
    def hset(self, key: str, mapping: Dict[str, Any] = None, **kwargs):
        if mapping:
            if key not in self.data:
                self.data[key] = {}
            self.data[key].update(mapping)
        if kwargs:
            if key not in self.data:
                self.data[key] = {}
            self.data[key].update(kwargs)
    
    def hgetall(self, key: str):
        return {k.encode(): v.encode() if isinstance(v, str) else str(v).encode() 
                for k, v in self.data.get(key, {}).items()}


def test_video_generation():
    """Prueba la generación de video localmente."""
    print("🧪 Iniciando prueba local de generación de video...")
    print("=" * 60)
    
    # Datos de prueba
    test_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos"
    }
    
    video_id = "test_" + str(int(__import__("time").time()))
    
    print(f"📝 Video ID: {video_id}")
    print(f"📋 Datos de prueba:")
    for key, value in test_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Verificar que los videos base existan
    assets_path = Path("assets")
    intro_video = assets_path / "Frames_1_2_to_3.mov"
    outro_video = assets_path / "Frame_4_NocheMagica.mov"
    
    if not intro_video.exists():
        print(f"❌ Error: No se encuentra {intro_video}")
        print(f"   Asegúrate de que los videos estén en: {assets_path.absolute()}")
        return False
    
    if not outro_video.exists():
        print(f"❌ Error: No se encuentra {outro_video}")
        return False
    
    print("✅ Videos base encontrados")
    print()
    
    # Verificar providers disponibles
    print("🔍 Verificando providers disponibles...")
    
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    print(f"   - TTS Providers: {len(manager.tts_providers)}")
    for provider in manager.tts_providers:
        print(f"     ✓ {provider.__class__.__name__}")
    
    print(f"   - Lip-sync Providers: {len(manager.lipsync_providers)}")
    for provider in manager.lipsync_providers:
        print(f"     ✓ {provider.__class__.__name__}")
    
    print(f"   - Video Providers: {len(manager.video_providers)}")
    for provider in manager.video_providers:
        print(f"     ✓ {provider.__class__.__name__}")
    
    if len(manager.video_providers) == 0 and len(manager.tts_providers) == 0:
        print()
        print("⚠️  Advertencia: No hay providers disponibles")
        print("   Configura al menos uno de:")
        print("   - ELEVENLABS_API_KEY (para TTS)")
        print("   - HEYGEN_API_KEY (para video completo)")
        print()
        return False
    
    print()
    
    # Procesar video
    try:
        print("🎬 Iniciando generación de video...")
        print()
        
        from providers.manager import ProviderManager
        import tempfile
        
        temp_dir = Path(tempfile.mkdtemp())
        output_path = temp_dir / "video_final.mp4"
        
        # Paths a videos
        intro_video_path = assets_path / "Frames_1_2_to_3.mov"
        outro_video_path = assets_path / "Frame_4_NocheMagica.mov"
        frame3_base = assets_path / "frame3_santa_base.mp4"  # Opcional
        
        # Scripts
        script_frame2 = "¡Ho, ho, ho! Mirá lo que tengo para vos..."
        script_frame3 = f"""
¡Hola {test_data['nombre']}! Soy Papá Noel y vengo desde el Polo Norte para saludarte en esta Noche Mágica.

Tu {test_data['parentesco']} me contó que este año {test_data['queHizo']}. ¡Qué orgullo me da saber eso!

{test_data['recuerdoEspecial']}

Y me dijeron que tu pedido especial para esta Noche Mágica es: {test_data['pedidoNocheMagica']}. 
Voy a hacer todo lo posible para que se cumpla.

Desde Grido y desde el Polo Norte, te deseamos unas Fiestas Mágicas llenas de alegría. 
Y recordá, la magia está en compartir... ¡y en un rico helado de Grido!

¡Ho, ho, ho! ¡Feliz Noche Mágica desde {test_data['provincia']}!
""".strip()
        
        # Procesar
        manager.process_video_with_fallback(
            intro_video=intro_video_path,
            base_video=frame3_base if frame3_base.exists() else intro_video_path,  # Fallback si no existe
            outro_video=outro_video_path,
            script_frame2=script_frame2,
            script_frame3=script_frame3,
            output_path=output_path,
            video_id=video_id,
        )
        
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # MB
            print()
            print("✅ Video generado exitosamente!")
            print(f"   📁 Ubicación: {output_path.absolute()}")
            print(f"   📊 Tamaño: {file_size:.2f} MB")
            print()
            
            # Intentar subir (si está configurado)
            try:
                from storage import upload_video
                video_url = upload_video(video_id, output_path)
                print(f"   🔗 URL: {video_url}")
            except Exception as e:
                print(f"   ⚠️  No se pudo subir (esperado en pruebas locales): {e}")
            
            return True
        else:
            print("❌ Error: El video no se generó")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("🚀 Prueba Local - Grido Video Worker")
    print("=" * 60)
    print()
    
    # Verificar que estamos en el directorio correcto
    if not Path("assets").exists():
        print("⚠️  Advertencia: No se encuentra el directorio 'assets'")
        print("   Asegúrate de ejecutar este script desde grido-backend/worker/")
        print()
    
    success = test_video_generation()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Prueba completada exitosamente!")
    else:
        print("❌ La prueba falló. Revisa los errores arriba.")
    print()


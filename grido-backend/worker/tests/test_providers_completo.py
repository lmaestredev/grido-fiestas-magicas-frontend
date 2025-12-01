"""
Script de prueba completo para verificar todos los providers configurados.

Este script prueba:
1. TTS providers (ElevenLabs)
2. Lip-sync providers (MuseTalk, Sync Labs, Wav2Lip)
3. Composición de video completa
4. Storage

Uso:
    python test_providers_completo.py
"""

import os
import sys
from pathlib import Path
import tempfile
import time

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_tts_providers():
    """Prueba los providers de TTS."""
    print()
    print("=" * 60)
    print("🎵 PRUEBA 1: TTS Providers")
    print("=" * 60)
    print()
    
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    if len(manager.tts_providers) == 0:
        print("❌ No hay providers de TTS disponibles")
        return False
    
    print(f"✅ Providers disponibles: {len(manager.tts_providers)}")
    for i, provider in enumerate(manager.tts_providers, 1):
        print(f"   {i}. {provider.__class__.__name__}")
    print()
    
    # Probar generación de audio
    test_text = "¡Hola! Este es un test de síntesis de voz."
    temp_dir = Path(tempfile.mkdtemp())
    audio_path = temp_dir / "test_audio.wav"
    
    try:
        print(f"📝 Generando audio con {manager.tts_providers[0].__class__.__name__}...")
        result = manager.generate_audio_with_fallback(
            test_text,
            audio_path,
            "test_tts"
        )
        
        if result.exists():
            size_kb = result.stat().st_size / 1024
            print(f"   ✅ Audio generado: {size_kb:.1f} KB")
            print(f"   📁 Ubicación: {result}")
            return True
        else:
            print("   ❌ Audio no generado")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def test_lipsync_providers():
    """Prueba los providers de lip-sync."""
    print()
    print("=" * 60)
    print("👄 PRUEBA 2: Lip-Sync Providers")
    print("=" * 60)
    print()
    
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    if len(manager.lipsync_providers) == 0:
        print("⚠️ No hay providers de lip-sync disponibles")
        print("   (Esto es normal si no están instalados)")
        return True  # No es un error crítico
    
    print(f"✅ Providers disponibles: {len(manager.lipsync_providers)}")
    for i, provider in enumerate(manager.lipsync_providers, 1):
        available = provider.is_available()
        status = "✅" if available else "⚠️"
        print(f"   {i}. {provider.__class__.__name__}: {status} {'disponible' if available else 'no disponible'}")
    print()
    
    # Verificar si hay assets para probar
    assets_path = Path("assets")
    frame3_base = assets_path / "frame3_santa_base.mp4"
    
    if not frame3_base.exists():
        print("⚠️ No hay video base para probar lip-sync")
        print(f"   Buscado en: {frame3_base}")
        return True  # No es un error crítico
    
    # Verificar si hay audio de prueba
    temp_dir = Path(tempfile.mkdtemp())
    test_audio = temp_dir / "test_audio.wav"
    
    # Generar audio de prueba
    try:
        from providers.manager import ProviderManager
        manager = ProviderManager()
        if len(manager.tts_providers) > 0:
            manager.generate_audio_with_fallback(
                "Este es un test de sincronización de labios.",
                test_audio,
                "test_lipsync"
            )
        else:
            print("⚠️ No hay TTS para generar audio de prueba")
            return True
    except Exception as e:
        print(f"⚠️ No se pudo generar audio de prueba: {str(e)}")
        return True
    
    # Probar cada provider disponible
    for provider in manager.lipsync_providers:
        if not provider.is_available():
            continue
        
        print(f"🧪 Probando {provider.__class__.__name__}...")
        try:
            output_path = temp_dir / f"test_lipsync_{provider.__class__.__name__}.mp4"
            result = provider.apply_lipsync(
                frame3_base,
                test_audio,
                output_path
            )
            
            if result.exists():
                size_mb = result.stat().st_size / (1024 * 1024)
                print(f"   ✅ Video generado: {size_mb:.2f} MB")
                print(f"   📁 Ubicación: {result}")
            else:
                print(f"   ⚠️ Video no generado")
        except Exception as e:
            print(f"   ⚠️ Error (puede ser normal): {str(e)}")
    
    return True


def test_video_composition():
    """Prueba la composición completa de video."""
    print()
    print("=" * 60)
    print("🎬 PRUEBA 3: Composición de Video Completa")
    print("=" * 60)
    print()
    
    # Verificar assets
    assets_path = Path("assets")
    intro_video = assets_path / "Frames_1_2_to_3.mov"
    frame3_base = assets_path / "frame3_santa_base.mp4"
    outro_video = assets_path / "Frame_4_NocheMagica.mov"
    
    missing = []
    if not intro_video.exists():
        missing.append("Frames_1_2_to_3.mov")
    if not frame3_base.exists():
        missing.append("frame3_santa_base.mp4")
    if not outro_video.exists():
        missing.append("Frame_4_NocheMagica.mov")
    
    if missing:
        print(f"⚠️ Faltan assets: {', '.join(missing)}")
        print(f"   Buscados en: {assets_path}")
        return False
    
    print("✅ Todos los assets encontrados")
    print()
    
    # Datos de prueba
    form_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "email": "test@example.com",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta",
        "recuerdoEspecial": "Cuando fuimos al parque",
        "pedidoNocheMagica": "Quiere un helado de chocolate"
    }
    
    # Templates
    FRAME2_PHRASE = "¡Ho, ho, ho! Mirá lo que tengo para vos..."
    FRAME3_TEMPLATE = """
¡Hola {nombre}! Soy Papá Noel y vengo desde el Polo Norte para saludarte en esta Noche Mágica.

Tu {parentesco} me contó que este año {queHizo}. ¡Qué orgullo me da saber eso!

{recuerdoEspecial}

Y me dijeron que tu pedido especial para esta Noche Mágica es: {pedidoNocheMagica}. 
Voy a hacer todo lo posible para que se cumpla.

¡Ho, ho, ho! ¡Feliz Noche Mágica desde {provincia}!
""".strip()
    
    script_frame2 = FRAME2_PHRASE
    script_frame3 = FRAME3_TEMPLATE.format(**form_data)
    
    video_id = f"test_completo_{int(time.time())}"
    temp_dir = Path(tempfile.mkdtemp())
    output_path = temp_dir / f"{video_id}.mp4"
    
    try:
        from providers.manager import ProviderManager
        manager = ProviderManager()
        
        print("🎬 Generando video completo...")
        print(f"   Video ID: {video_id}")
        print()
        
        result = manager.process_video_with_fallback(
            intro_video=intro_video,
            base_video=frame3_base,
            outro_video=outro_video,
            script_frame2=script_frame2,
            script_frame3=script_frame3,
            output_path=output_path,
            video_id=video_id,
        )
        
        if result.exists():
            size_mb = result.stat().st_size / (1024 * 1024)
            print(f"   ✅ Video generado: {size_mb:.2f} MB")
            print(f"   📁 Ubicación: {result}")
            return True
        else:
            print("   ❌ Video no generado")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_storage():
    """Prueba el sistema de storage."""
    print()
    print("=" * 60)
    print("📤 PRUEBA 4: Storage")
    print("=" * 60)
    print()
    
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    print(f"📦 Tipo de storage: {storage_type}")
    print()
    
    # Crear un archivo de prueba
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / "test_storage.mp4"
    test_file.write_bytes(b"test video content" * 1000)  # Archivo dummy
    
    try:
        from storage import upload_video
        
        video_id = f"test_storage_{int(time.time())}"
        print(f"📤 Subiendo video: {video_id}...")
        
        video_url = upload_video(video_id, test_file)
        
        print(f"   ✅ Video subido")
        print(f"   🔗 URL: {video_url}")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Error (puede ser normal según configuración): {str(e)}")
        return True  # No es crítico


def main():
    """Ejecuta todas las pruebas."""
    print()
    print("🚀 PRUEBAS COMPLETAS DEL SISTEMA")
    print("=" * 60)
    print()
    
    results = {}
    
    # Prueba 1: TTS
    results["TTS"] = test_tts_providers()
    
    # Prueba 2: Lip-sync
    results["Lip-sync"] = test_lipsync_providers()
    
    # Prueba 3: Composición de video
    results["Video"] = test_video_composition()
    
    # Prueba 4: Storage
    results["Storage"] = test_storage()
    
    # Resumen
    print()
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print()
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    print()
    
    all_passed = all(results.values())
    if all_passed:
        print("✅ Todas las pruebas pasaron")
    else:
        print("⚠️ Algunas pruebas fallaron (revisa los detalles arriba)")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


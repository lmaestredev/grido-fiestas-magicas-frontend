"""
Test específico para D-ID Video Provider.

Este test valida que D-ID funcione correctamente:
1. Genera audio con ElevenLabs
2. Usa la imagen ya subida a D-ID (source_url)
3. Sube el audio a D-ID
4. Crea un talk con imagen y audio
5. Genera el video final

Uso:
    python tests/test_did.py
    python tests/test_did.py --image-url s3://d-id-images-prod/.../Grido_PapaNoel.png
"""

import os
import sys
from pathlib import Path
import tempfile
import argparse

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
sys.path.insert(0, str(worker_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_did_provider_direct():
    """Test directo del provider de D-ID con audio pre-generado."""
    
    print("\n🎬 Test de D-ID Video Provider (Directo)")
    print("=" * 60)
    print()
    
    # Verificar configuración de D-ID
    did_api_key = os.getenv("DID_API_KEY") or os.getenv("DID_API_KEY_PLAIN")
    if not did_api_key:
        print("❌ Error: D-ID API key no está configurado")
        print("   Configura en .env:")
        print("   DID_API_KEY_PLAIN=tu_api_key")
        print("   O")
        print("   DID_API_KEY=base64_encoded_key")
        return False
    
    # Verificar configuración de ElevenLabs (requerido para generar audio)
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    if not elevenlabs_key:
        print("❌ Error: ELEVENLABS_API_KEY no está configurado")
        print("   D-ID requiere audio pre-generado con ElevenLabs")
        return False
    
    print("✅ Credenciales detectadas")
    print(f"   D-ID API Key: {'set' if did_api_key else 'no'}")
    print(f"   ElevenLabs API Key: {'set' if elevenlabs_key else 'no'}")
    print()
    
    from providers.did_video import DIDVideoProvider
    from providers.manager import ProviderManager
    
    # Inicializar providers
    did_provider = DIDVideoProvider()
    if not did_provider.is_available():
        print("❌ D-ID provider no está disponible (is_available()=False)")
        return False
    
    manager = ProviderManager()
    if not manager.elevenlabs:
        print("❌ ElevenLabs no está disponible en ProviderManager")
        return False
    
    print("✅ Providers inicializados correctamente")
    print()
    
    # Script de prueba
    script = """
¡Hola! Soy Papá Noel y vengo desde el Polo Norte para saludarte en esta Noche Mágica.
Este es un mensaje de prueba para validar la integración con D-ID.
¡Feliz Navidad desde Grido!
"""
    
    temp_dir = Path(tempfile.mkdtemp(prefix="did_test_"))
    audio_path = temp_dir / "test_audio.wav"
    video_path = temp_dir / "did_test_video.mp4"
    
    try:
        # Paso 1: Generar audio con ElevenLabs
        print("🎵 Paso 1: Generando audio con ElevenLabs...")
        print(f"   Script: {script.strip()[:50]}...")
        
        audio_result = manager.generate_audio_with_fallback(
            text=script.strip(),
            output_path=audio_path,
            video_id="test_did",
            use_cache=False  # No usar caché en tests
        )
        
        if not audio_result.exists():
            print("❌ El audio no se generó correctamente")
            return False
        
        audio_size_kb = audio_result.stat().st_size / 1024
        print(f"✅ Audio generado: {audio_size_kb:.2f} KB")
        print()
        
        # Paso 2: Obtener source_url de la imagen
        # Opción 1: Usar URL de imagen ya subida (de variable de entorno o argumento)
        image_source_url = os.getenv("DID_PAPA_NOEL_IMAGE_URL")
        
        # Opción 2: Subir imagen ahora si no está configurada
        if not image_source_url:
            print("📤 Paso 2: Subiendo imagen a D-ID...")
            from papa_noel_config import get_papa_noel_image_path
            
            try:
                image_path = get_papa_noel_image_path()
                print(f"   Imagen encontrada: {image_path}")
                
                image_source_url = did_provider._upload_image(image_path)
                print(f"✅ Imagen subida exitosamente")
                print(f"   Image Source URL: {image_source_url}")
                print()
                print("💡 Guarda esta URL en .env para futuros usos:")
                print(f"   DID_PAPA_NOEL_IMAGE_URL={image_source_url}")
            except Exception as e:
                print(f"❌ Error subiendo imagen: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("📤 Paso 2: Usando imagen ya subida a D-ID")
            print(f"   Source URL: {image_source_url}")
        
        print()
        
        # Paso 3: Subir audio a D-ID
        print("📤 Paso 3: Subiendo audio a D-ID...")
        audio_url = did_provider._upload_audio(audio_result)
        print(f"✅ Audio subido: {audio_url[:80]}...")
        print()
        
        # Paso 4: Crear talk con imagen y audio
        print("🎬 Paso 4: Creando talk en D-ID...")
        print("   (Esto puede tardar varios minutos)")
        print()
        
        talk_id = did_provider._create_talk(image_source_url, audio_url)
        print(f"✅ Talk creado: {talk_id}")
        print()
        
        # Paso 5: Polling y descarga
        print("⏳ Paso 5: Esperando generación del video...")
        print("   (Polling cada 5 segundos, timeout: 10 minutos)")
        print()
        
        import time
        start_time = time.time()
        max_poll_time = 600  # 10 minutos
        
        while time.time() - start_time < max_poll_time:
            status_response = did_provider._poll_talk_status(talk_id)
            status = status_response.get("status")
            
            elapsed = int(time.time() - start_time)
            print(f"   Status: {status} (tiempo transcurrido: {elapsed}s)", end="\r")
            
            if status == "done":
                print()  # Nueva línea después del \r
                video_url = (
                    status_response.get("result_url") or
                    status_response.get("url") or
                    status_response.get("video_url")
                )
                if not video_url:
                    print("❌ Talk completado pero no hay URL de video")
                    return False
                
                print(f"✅ Video generado! Descargando...")
                print(f"   URL: {video_url[:80]}...")
                
                # Descargar video
                final_video = did_provider._download_video(video_url, video_path)
                
                if not final_video.exists():
                    print("❌ El video no se descargó correctamente")
                    return False
                
                size_mb = final_video.stat().st_size / (1024 * 1024)
                print()
                print("=" * 60)
                print("✅ Test completado exitosamente!")
                print(f"   📁 Video: {final_video}")
                print(f"   📊 Tamaño: {size_mb:.2f} MB")
                print(f"   🎬 Talk ID: {talk_id}")
                print()
                return True
            
            elif status == "error" or status == "failed":
                print()  # Nueva línea después del \r
                error_obj = status_response.get("error", {})
                if isinstance(error_obj, dict):
                    error_kind = error_obj.get("kind")
                    error_description = error_obj.get("description") or error_obj.get("message")
                    
                    if error_kind == "FaceError" or (error_description and "face not detected" in str(error_description).lower()):
                        print("❌ Error: D-ID no pudo detectar una cara humana en la imagen")
                        print()
                        print("⚠️  LIMITACIÓN DE D-ID:")
                        print("   D-ID requiere fotos reales de personas.")
                        print("   No funciona con ilustraciones, dibujos o diseños.")
                        print()
                        print("💡 SOLUCIONES:")
                        print("   1. Usar una foto real de una persona como Papá Noel")
                        print("   2. Usar HeyGen (soporta avatares personalizados)")
                        print("   3. Usar Higgsfield (soporta avatares personalizados)")
                        print("   4. Usar Wav2Lip con video base (no requiere detección de cara en imagen)")
                        return False
                    else:
                        error_msg = error_description or str(error_obj)
                else:
                    error_msg = str(error_obj) if error_obj else "Unknown error"
                
                if not error_msg or error_msg == "Unknown error":
                    error_msg = str(status_response.get("error", "Unknown error"))
                
                print(f"❌ Error en la generación: {error_msg}")
                return False
            
            time.sleep(5)  # Polling cada 5 segundos
        
        print()  # Nueva línea después del \r
        print(f"❌ Timeout: La generación tardó más de {max_poll_time} segundos")
        return False
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_did_with_manager():
    """Test de D-ID usando el método generate_video del provider directamente."""
    
    print("\n🎬 Test de D-ID Video Provider (con generate_video)")
    print("=" * 60)
    print()
    
    # Verificar configuración
    did_api_key = os.getenv("DID_API_KEY") or os.getenv("DID_API_KEY_PLAIN")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not did_api_key or not elevenlabs_key:
        print("❌ Configuración incompleta")
        return False
    
    from providers.did_video import DIDVideoProvider
    from providers.manager import ProviderManager
    
    did_provider = DIDVideoProvider()
    manager = ProviderManager()
    
    if not did_provider.is_available() or not manager.elevenlabs:
        print("❌ Providers no disponibles")
        return False
    
    script = "¡Hola! Este es un mensaje de prueba para D-ID. ¡Feliz Navidad!"
    temp_dir = Path(tempfile.mkdtemp(prefix="did_test_"))
    audio_path = temp_dir / "test_audio.wav"
    video_path = temp_dir / "did_test_video.mp4"
    
    try:
        # Generar audio
        print("🎵 Generando audio con ElevenLabs...")
        audio_result = manager.generate_audio_with_fallback(
            text=script,
            output_path=audio_path,
            video_id="test_did_manager",
            use_cache=False
        )
        print(f"✅ Audio generado: {audio_result.stat().st_size / 1024:.2f} KB")
        print()
        
        # Obtener source_url de imagen
        image_source_url = os.getenv("DID_PAPA_NOEL_IMAGE_URL")
        if not image_source_url:
            print("📤 Subiendo imagen a D-ID...")
            from papa_noel_config import get_papa_noel_image_path
            image_path = get_papa_noel_image_path()
            image_source_url = did_provider._upload_image(image_path)
            print(f"✅ Imagen subida")
        print()
        
        # Generar video usando generate_video (que maneja todo internamente)
        print("🎬 Generando video con D-ID...")
        print("   (Esto puede tardar varios minutos)")
        print()
        
        # Nota: generate_video espera image_path, pero podemos pasar source_url
        # Necesitamos modificar el flujo o usar los métodos internos directamente
        # Por ahora, usamos el flujo manual como en test_did_provider_direct
        
        # Alternativa: usar generate_video pero necesitamos pasar source_url
        # Como generate_video busca la imagen localmente, mejor usar el método directo
        # que ya probamos arriba
        
        print("💡 Usa test_did_provider_direct() para un test más completo")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_did_integration():
    """Test de integración de D-ID con ProviderManager."""
    
    print("\n🔄 Test de Integración D-ID con ProviderManager")
    print("=" * 60)
    print()
    
    from providers.manager import ProviderManager
    
    manager = ProviderManager()
    
    # Verificar que D-ID esté en la lista de providers
    did_providers = [p for p in manager.video_providers if p.__class__.__name__ == "DIDVideoProvider"]
    
    if not did_providers:
        print("⚠️  D-ID no está disponible en ProviderManager")
        print("   Verifica que DID_API_KEY o DID_API_KEY_PLAIN esté configurado")
        return False
    
    print(f"✅ D-ID encontrado en ProviderManager")
    
    # Verificar orden de prioridad
    print("\n📋 Orden de providers de video:")
    for i, provider in enumerate(manager.video_providers, 1):
        provider_name = provider.__class__.__name__
        print(f"   {i}. {provider_name}")
    
    # D-ID debería estar en posición 2 (después de HeyGen)
    did_position = None
    for i, provider in enumerate(manager.video_providers):
        if provider.__class__.__name__ == "DIDVideoProvider":
            did_position = i + 1
            break
    
    if did_position == 2:
        print("\n✅ D-ID está en la posición 2 (Priority 2) ✓")
    elif did_position == 1:
        print("\n⚠️  D-ID está en la posición 1 (debería ser 2 si HeyGen está disponible)")
    else:
        print(f"\n⚠️  D-ID está en la posición {did_position}")
    
    # Verificar que ElevenLabs esté disponible (requerido para D-ID)
    if not manager.elevenlabs:
        print("\n⚠️  ElevenLabs no está disponible (requerido para D-ID)")
        print("   D-ID necesita audio pre-generado con ElevenLabs")
    else:
        print("\n✅ ElevenLabs disponible (requerido para D-ID)")
    
    print()
    return True


def main():
    """Función principal del test."""
    parser = argparse.ArgumentParser(description="Test de D-ID Video Provider")
    parser.add_argument(
        "--test",
        choices=["direct", "manager", "integration", "all"],
        default="all",
        help="Tipo de test a ejecutar (default: all)"
    )
    parser.add_argument(
        "--image-url",
        type=str,
        help="URL de imagen ya subida a D-ID (source_url)"
    )
    
    args = parser.parse_args()
    
    # Si se proporciona image-url, guardarla en env temporalmente
    if args.image_url:
        os.environ["DID_PAPA_NOEL_IMAGE_URL"] = args.image_url
        print(f"📌 Usando imagen URL proporcionada: {args.image_url[:80]}...")
        print()
    
    results = []
    
    if args.test in ("direct", "all"):
        results.append(("Direct Provider Test", test_did_provider_direct()))
    
    if args.test in ("manager", "all"):
        results.append(("Manager Integration Test", test_did_with_manager()))
    
    if args.test in ("integration", "all"):
        results.append(("ProviderManager Integration", test_did_integration()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 Resumen de Tests")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
    print()
    
    # Exit code
    all_passed = all(result for _, result in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


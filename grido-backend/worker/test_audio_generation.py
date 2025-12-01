"""
Script de prueba para generación de audio con voz de Papá Noel.

Este script prueba la generación de audio usando los datos del formulario
y asegura que siempre se use la misma voz de Papá Noel.

Uso:
    python test_audio_generation.py
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

def test_audio_generation():
    """Prueba la generación de audio con datos del formulario."""
    print()
    print("🎤 Prueba de Generación de Audio - Papá Noel")
    print("=" * 60)
    print()
    
    # Datos simulados del formulario
    test_data = {
        "nombre": "Juan",
        "parentesco": "papá",
        "provincia": "Buenos Aires",
        "queHizo": "Aprendió a andar en bicicleta y fue al jardín todos los días",
        "recuerdoEspecial": "Cuando fuimos al parque y se rió mucho en los columpios",
        "pedidoNocheMagica": "Quiere un helado de chocolate y jugar con sus amigos"
    }
    
    print("📝 Datos del formulario:")
    for key, value in test_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Template del script (igual que en video-worker.py)
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
    
    print("📜 Scripts generados:")
    print(f"   Frame 2: {script_frame2}")
    print(f"   Frame 3: {script_frame3[:100]}...")
    print()
    
    # Verificar providers disponibles
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    if len(manager.tts_providers) == 0:
        print("❌ Error: No hay providers de TTS disponibles")
        print("   Configura al menos uno de:")
        print("   - ELEVENLABS_API_KEY")
        print("   - KOKORO_MODEL_PATH")
        return False
    
    print(f"✅ Providers de TTS disponibles: {len(manager.tts_providers)}")
    for provider in manager.tts_providers:
        print(f"   - {provider.__class__.__name__}")
        if hasattr(provider, 'voice_id'):
            print(f"     Voz: {provider.voice_id}")
    print()
    
    # Crear directorio temporal
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        # Generar audio para Frame 2
        print("🎵 Generando audio para Frame 2...")
        audio_frame2 = temp_dir / "audio_frame2.wav"
        manager.generate_audio_with_fallback(
            script_frame2,
            audio_frame2,
            video_id="test_audio"
        )
        
        if audio_frame2.exists():
            size_mb = audio_frame2.stat().st_size / (1024 * 1024)
            print(f"   ✅ Audio generado: {audio_frame2}")
            print(f"   📊 Tamaño: {size_mb:.2f} MB")
        else:
            print("   ❌ Error: Audio no generado")
            return False
        
        print()
        
        # Generar audio para Frame 3
        print("🎵 Generando audio para Frame 3...")
        audio_frame3 = temp_dir / "audio_frame3.wav"
        manager.generate_audio_with_fallback(
            script_frame3,
            audio_frame3,
            video_id="test_audio"
        )
        
        if audio_frame3.exists():
            size_mb = audio_frame3.stat().st_size / (1024 * 1024)
            print(f"   ✅ Audio generado: {audio_frame3}")
            print(f"   📊 Tamaño: {size_mb:.2f} MB")
        else:
            print("   ❌ Error: Audio no generado")
            return False
        
        print()
        print("=" * 60)
        print("✅ Prueba de generación de audio completada exitosamente!")
        print()
        print("📁 Archivos generados:")
        print(f"   - {audio_frame2}")
        print(f"   - {audio_frame3}")
        print()
        print("💡 Para reproducir:")
        print(f"   open {audio_frame2}")
        print(f"   open {audio_frame3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la generación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_audio_generation()
    sys.exit(0 if success else 1)


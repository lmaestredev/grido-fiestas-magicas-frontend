"""
Script de prueba simplificado - Solo audio sobre video (sin lip-sync).

Este script prueba el flujo completo usando:
- ElevenLabs para TTS
- FFmpeg para agregar audio al video (sin lip-sync)
- Storage local

Uso:
    python test_flujo_simple.py
"""

import os
import sys
from pathlib import Path
import tempfile
import subprocess

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def add_audio_to_video(video_path: Path, audio_path: Path, output_path: Path) -> Path:
    """Agrega audio a un video usando FFmpeg."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Re-encodear video porque puede ser ProRes (no compatible con MP4 directo)
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "libx264",  # Re-encodear video a H.264
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",      # Codec de audio
        "-b:a", "128k",
        "-map", "0:v:0",    # Video del primer input
        "-map", "1:a:0",    # Audio del segundo input
        "-shortest",        # Terminar cuando el más corto termine
        "-pix_fmt", "yuv420p",  # Formato compatible
        "-y",               # Sobrescribir
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"FFmpeg failed: {result.stderr}")
    
    return output_path

def test_flujo_simple():
    """Prueba flujo simplificado sin lip-sync."""
    print()
    print("🚀 Prueba Flujo Simplificado - Audio sobre Video")
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
    
    video_id = f"test_simple_{int(__import__('time').time())}"
    
    print(f"📝 Video ID: {video_id}")
    print("📋 Datos del formulario:")
    for key, value in form_data.items():
        print(f"   - {key}: {value}")
    print()
    
    # Verificar assets
    assets_path = Path("assets")
    intro_video = assets_path / "Frames_1_2_to_3.mov"
    outro_video = assets_path / "Frame_4_NocheMagica.mov"
    frame3_base = assets_path / "frame3_santa_base.mp4"
    
    if not all([intro_video.exists(), outro_video.exists()]):
        print("❌ Error: Faltan videos base")
        return False
    
    print("✅ Videos base encontrados")
    print()
    
    # Verificar ElevenLabs
    from providers.manager import ProviderManager
    manager = ProviderManager()
    
    if len(manager.tts_providers) == 0:
        print("❌ Error: No hay providers de TTS")
        return False
    
    print(f"✅ TTS Provider: {manager.tts_providers[0].__class__.__name__}")
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
    temp_dir = Path(tempfile.mkdtemp())
    
    try:
        print("🎵 Paso 1: Generando audios...")
        
        # Generar audio Frame 2
        audio_frame2 = temp_dir / "audio_frame2.wav"
        manager.generate_audio_with_fallback(script_frame2, audio_frame2, video_id)
        print(f"   ✅ Audio Frame 2: {audio_frame2.stat().st_size / 1024:.1f} KB")
        
        # Generar audio Frame 3
        audio_frame3 = temp_dir / "audio_frame3.wav"
        manager.generate_audio_with_fallback(script_frame3, audio_frame3, video_id)
        print(f"   ✅ Audio Frame 3: {audio_frame3.stat().st_size / 1024:.1f} KB")
        print()
        
        print("🎬 Paso 2: Agregando audio a videos...")
        
        # Agregar audio a intro (Frame 2)
        intro_with_audio = temp_dir / "intro_with_audio.mp4"
        add_audio_to_video(intro_video, audio_frame2, intro_with_audio)
        print(f"   ✅ Intro con audio")
        
        # Agregar audio a frame3 (Frame 3)
        frame3_with_audio = temp_dir / "frame3_with_audio.mp4"
        if frame3_base.exists():
            add_audio_to_video(frame3_base, audio_frame3, frame3_with_audio)
        else:
            # Si no existe frame3, usar intro como base
            add_audio_to_video(intro_video, audio_frame3, frame3_with_audio)
        print(f"   ✅ Frame 3 con audio")
        print()
        
        print("🎞️  Paso 3: Componiendo video final...")
        
        # Componer video final (intro + frame3 + outro)
        final_video = temp_dir / "video_final.mp4"
        
        # Crear lista de archivos para FFmpeg concat
        concat_list = temp_dir / "concat_list.txt"
        with open(concat_list, "w") as f:
            f.write(f"file '{intro_with_audio.absolute()}\n")
            f.write(f"file '{frame3_with_audio.absolute()}\n")
            f.write(f"file '{outro_video.absolute()}\n")
        
        # Concatenar videos
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            "-y",
            str(final_video)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            # Si falla con copy, usar re-encoding
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-y",
                str(final_video)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        
        if not final_video.exists():
            print("❌ Error: Video final no generado")
            return False
        
        file_size = final_video.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ Video final: {file_size:.2f} MB")
        print()
        
        print("📤 Paso 4: Subiendo a storage...")
        from storage import upload_video
        video_url = upload_video(video_id, final_video)
        print(f"   ✅ Video subido")
        print(f"   🔗 URL: {video_url}")
        print()
        
        print("=" * 60)
        print("✅ Prueba completada exitosamente!")
        print()
        print("📊 Resumen:")
        print(f"   - Video ID: {video_id}")
        print(f"   - Tamaño: {file_size:.2f} MB")
        print(f"   - URL: {video_url}")
        print()
        
        if video_url.startswith("file://"):
            local_path = video_url.replace("file://", "")
            print("💡 Para reproducir:")
            print(f"   open {local_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_flujo_simple()
    sys.exit(0 if success else 1)


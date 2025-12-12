"""
Modal Worker para Grido Fiestas Mágicas

Este worker corre en Modal con GPU y procesa videos desde una cola Redis.
"""

import modal
import os
import json
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definir imagen de Docker con todas las dependencias
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install(
        "redis",
        "boto3",
        "requests",
        "httpx",
        "torch",
        "torchvision",
        "torchaudio",
        "numpy",
        "opencv-python",
        "librosa",
        "soundfile",
    )
    # Copy providers directory to image
    .copy_local_dir("providers", "/root/providers")
    # Instalar Kokoro TTS (ajustar según tu implementación)
    # .run_commands("pip install git+https://github.com/hexgrad/kokoro.git")
)

# Crear stub de Modal
stub = modal.Stub("grido-video-worker", image=image)

# Montar assets como volumen
assets_volume = modal.NetworkFileSystem.persisted("grido-assets")

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
"""


def log(video_id: str, message: str):
    """Helper para logging"""
    print(f"[{video_id}] {message}")


# ProviderManager will be imported and initialized in process_video function


def add_audio_to_intro(video_id: str, intro_video: Path, audio: Path, temp_dir: Path) -> Path:
    """Añade audio al video INTRO."""
    output_path = temp_dir / "intro_with_audio.mp4"
    
    log(video_id, "Añadiendo audio al INTRO...")
    
    subprocess.run([
        "ffmpeg", "-i", str(intro_video), "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-y", str(output_path)
    ], check=True, capture_output=True)
    
    return output_path


def concatenate_videos(video_id: str, intro: Path, middle: Path, outro: Path, temp_dir: Path) -> Path:
    """Concatena los 3 videos."""
    output_path = temp_dir / "video_final.mp4"
    concat_list = temp_dir / "concat_list.txt"
    
    log(video_id, "Concatenando videos...")
    
    with open(concat_list, "w") as f:
        f.write(f"file '{intro.absolute()}'\n")
        f.write(f"file '{middle.absolute()}'\n")
        f.write(f"file '{outro.absolute()}'\n")
    
    # Intentar sin re-encoding
    result = subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", "-y", str(output_path)
    ], capture_output=True)
    
    # Si falla, re-encodear
    if result.returncode != 0:
        subprocess.run([
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", "-y", str(output_path)
        ], check=True, capture_output=True)
    
    return output_path


def upload_to_r2(video_id: str, file_path: Path) -> str:
    """Sube video usando el storage provider configurado."""
    from storage import upload_video
    return upload_video(video_id, file_path)


def send_email(video_id: str, to_email: str, nombre: str, video_url: str):
    """Envía email con Resend."""
    import requests
    
    log(video_id, f"Enviando email a {to_email}...")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #0033A0; text-align: center;">¡Tu Saludo Mágico está listo!</h1>
        <p style="font-size: 16px;">Hola {nombre},</p>
        <p style="font-size: 16px;">
            Tu Saludo Mágico de Papá Noel está listo para compartir. 
            ¡Hacé clic en el botón para verlo!
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{video_url}" 
               style="background-color: #0033A0; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px; font-size: 18px; 
                      display: inline-block;">
                Ver mi Video Mágico
            </a>
        </div>
        <p style="font-size: 14px; color: #666;">
            ¡Felices Fiestas Mágicas de parte de Grido! 🎄✨
        </p>
    </body>
    </html>
    """
    
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {os.environ['RESEND_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Grido Fiestas Mágicas <noreply@grido.com>",
            "to": [to_email],
            "subject": "¡Tu Saludo Mágico de Papá Noel está listo! 🎄",
            "html": html_body,
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to send email: {response.text}")
    
    log(video_id, "Email enviado")


@stub.function(
    gpu="T4",  # o "A10G" para más potencia
    secrets=[modal.Secret.from_name("grido-secrets")],
    network_file_systems={"/assets": assets_volume},
    timeout=600,  # 10 minutos
)
def process_video(video_id: str, data: dict):
    """
    Procesa un video completo.
    
    Esta función se ejecuta en Modal con GPU.
    """
    import redis
    
    # Conectar a Redis
    redis_client = redis.from_url(os.environ['REDIS_URL'])
    
    # Crear directorio temporal
    temp_dir = Path("/tmp") / video_id
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        log(video_id, "Iniciando procesamiento...")
        
        # Actualizar estado
        redis_client.hset(f"job:{video_id}", "status", "processing")
        
        # Import ProviderManager (import here to avoid issues with Modal)
        import sys
        sys.path.insert(0, "/root")
        from providers.manager import ProviderManager
        
        # Initialize provider manager
        manager = ProviderManager()
        
        # Prepare script for frame 3
        script_frame3 = FRAME3_TEMPLATE.format(**data)
        
        # Paths to assets (usando videos .mov para mantener transparencia)
        intro_base = Path("/assets/Frames_1_2_to_3.mov")
        frame3_base = Path("/assets/frame3_santa_base.mp4")  # Solo usado en Strategy 1 (lip-sync)
        outro = Path("/assets/Frame_4_NocheMagica.mov")
        
        # Final video path
        final_video = temp_dir / "video_final.mp4"
        
        # Use ProviderManager to process video with fallback
        manager.process_video_with_fallback(
            intro_video=intro_base,
            base_video=frame3_base,
            outro_video=outro,
            script_frame2=FRAME2_PHRASE,
            script_frame3=script_frame3,
            output_path=final_video,
            video_id=video_id,
        )
        
        # PASO 6: Subir a R2
        # Subir video (Firebase/Vercel/Railway/S3/R2/Local según STORAGE_TYPE)
        video_url = upload_to_r2(video_id, final_video)
        
        # PASO 7: Enviar email
        send_email(video_id, data["email"], data["nombre"], video_url)
        
        # Actualizar estado
        redis_client.hset(f"job:{video_id}", mapping={
            "status": "completed",
            "videoUrl": video_url,
            "completedAt": str(time.time())
        })
        
        log(video_id, "Completado")
        
        return {"success": True, "videoUrl": video_url}
        
    except Exception as e:
        log(video_id, f"Error: {str(e)}")
        redis_client.hset(f"job:{video_id}", mapping={
            "status": "failed",
            "error": str(e),
            "failedAt": str(time.time())
        })
        raise


@stub.local_entrypoint()
def main():
    """
    Loop principal que escucha la cola de Redis.
    
    Ejecutar localmente con: modal run modal_worker.py
    O deployar con: modal deploy modal_worker.py
    """
    import redis
    
    redis_client = redis.from_url(os.environ['REDIS_URL'])
    
    print("Worker iniciado, esperando trabajos...")
    
    while True:
        try:
            # Esperar trabajo de la cola
            result = redis_client.brpop("video:queue", timeout=5)
            
            if result:
                _, video_id = result
                video_id = video_id.decode('utf-8')
                
                # Obtener datos del job
                job_data = redis_client.hgetall(f"job:{video_id}")
                if not job_data:
                    print(f"[{video_id}] Job no encontrado")
                    continue
                
                # Decodificar datos
                data = json.loads(job_data[b"data"].decode('utf-8'))
                
                # Procesar en Modal (remoto)
                process_video.remote(video_id, data)
                
        except KeyboardInterrupt:
            print("\n Worker detenido")
            break
        except Exception as e:
            print(f" Error: {str(e)}")
            time.sleep(5)

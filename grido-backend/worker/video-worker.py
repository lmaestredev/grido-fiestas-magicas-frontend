"""
Video Generation Worker para Grido Fiestas Mágicas

Este worker procesa videos de forma asíncrona desde una cola Redis.
Genera audios con TTS, aplica lip-sync y compone el video final.
"""

import os
import json
import subprocess
import time
import logging
from pathlib import Path
import redis
import boto3
from typing import Dict, Any
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
S3_BUCKET = os.getenv("S3_BUCKET", "grido-papa-noel-videos")
S3_REGION = os.getenv("AWS_REGION", "us-east-1")
ASSETS_PATH = Path("assets")
TEMP_DIR = Path("/tmp/grido_videos")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Conectar a Redis
redis_client = redis.from_url(REDIS_URL)

# Cliente S3
s3_client = boto3.client('s3', region_name=S3_REGION)

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


def update_job_status(video_id: str, status: str, data: Dict[str, Any] = None):
    """Actualiza el estado del job en Redis"""
    job_key = f"job:{video_id}"
    job_data = redis_client.get(job_key)
    
    if job_data:
        job = json.loads(job_data)
        job["status"] = status
        job["updatedAt"] = time.time()
        
        if data:
            job.update(data)
        
        redis_client.set(job_key, json.dumps(job))


# ProviderManager will be used instead of these functions


def add_audio_to_intro(video_id: str, intro_video: Path, audio: Path) -> Path:
    """
    Añade audio al video INTRO (Frame 1+2).
    
    Args:
        video_id: ID del video
        intro_video: Path al video intro sin audio
        audio: Path al audio del Frame 2
    
    Returns:
        Path al video intro con audio
    """
    output_path = TEMP_DIR / video_id / "intro_with_audio.mp4"
    
    log(video_id, "Añadiendo audio al INTRO...")
    
    cmd = [
        "ffmpeg",
        "-i", str(intro_video),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-y", str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    log(video_id, f"INTRO con audio: {output_path}")
    return output_path


def concatenate_videos(video_id: str, intro: Path, middle: Path, outro: Path) -> Path:
    """
    Concatena los 3 videos finales.
    
    Args:
        video_id: ID del video
        intro: Path al video intro
        middle: Path al video middle (Frame 3)
        outro: Path al video outro
    
    Returns:
        Path al video final
    """
    output_path = TEMP_DIR / video_id / "video_final.mp4"
    concat_list = TEMP_DIR / video_id / "concat_list.txt"
    
    log(video_id, "Concatenando videos...")
    
    # Crear lista de concatenación
    with open(concat_list, "w") as f:
        f.write(f"file '{intro.absolute()}'\n")
        f.write(f"file '{middle.absolute()}'\n")
        f.write(f"file '{outro.absolute()}'\n")
    
    # Intentar concatenar sin re-encoding
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        "-y", str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    # Si falla, hacer re-encoding
    if result.returncode != 0:
        log(video_id, "Concatenación con copy falló, usando re-encoding...")
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
            "-y", str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    
    log(video_id, f"Video final: {output_path}")
    return output_path


def upload_to_s3(video_id: str, file_path: Path) -> str:
    """
    Sube el video a S3 y retorna la URL pública.
    
    Args:
        video_id: ID del video
        file_path: Path al archivo a subir
    
    Returns:
        URL pública del video
    """
    log(video_id, "Subiendo video a S3...")
    
    s3_key = f"videos/{video_id}.mp4"
    
    s3_client.upload_file(
        str(file_path),
        S3_BUCKET,
        s3_key,
        ExtraArgs={'ContentType': 'video/mp4'}
    )
    
    video_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
    
    log(video_id, f"Video subido: {video_url}")
    return video_url


def send_email(video_id: str, to_email: str, nombre: str, video_url: str):
    """
    Envía el email con el link al video usando Resend.
    
    Args:
        video_id: ID del video
        to_email: Email del destinatario
        nombre: Nombre del destinatario
        video_url: URL del video
    """
    log(video_id, f"Enviando email a {to_email}...")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #0033A0;">¡Tu Saludo Mágico está listo!</h1>
        </div>
        
        <p style="font-size: 16px; line-height: 1.6;">Hola {nombre},</p>
        
        <p style="font-size: 16px; line-height: 1.6;">
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
        
        <p style="font-size: 14px; color: #666; margin-top: 30px;">
            ¡Felices Fiestas Mágicas de parte de Grido! 🎄✨
        </p>
    </body>
    </html>
    """
    
    # Enviar con Resend
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Grido Fiestas Mágicas <noreply@grido.com>",
            "to": [to_email],
            "subject": "¡Tu Saludo Mágico de Papá Noel está listo! 🎄",
            "html": html_body,
        }
    )
    
    if response.status_code == 200:
        log(video_id, "Email enviado exitosamente")
    else:
        log(video_id, f"Error enviando email: {response.text}")
        raise Exception("Failed to send email")


def process_video(video_id: str, data: Dict[str, Any]):
    """
    Procesa un video completo.
    
    Args:
        video_id: ID del video
        data: Datos del formulario
    """
    try:
        log(video_id, "Iniciando procesamiento...")
        update_job_status(video_id, "processing")
        
        # Crear directorio temporal
        temp_dir = TEMP_DIR / video_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Import ProviderManager
        from providers.manager import ProviderManager
        
        # Initialize provider manager
        manager = ProviderManager()
        
        # Prepare script for frame 3
        script_frame3 = FRAME3_TEMPLATE.format(**data)
        
        # Paths to assets
        intro_base = ASSETS_PATH / "intro_frames1_2.mp4"
        frame3_base = ASSETS_PATH / "frame3_santa_base.mp4"
        outro = ASSETS_PATH / "outro_frame4.mp4"
        
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
        
        # PASO 6: Subir a S3
        video_url = upload_to_s3(video_id, final_video)
        
        # PASO 7: Enviar email
        send_email(video_id, data["email"], data["nombre"], video_url)
        
        # Actualizar estado
        update_job_status(video_id, "completed", {
            "videoUrl": video_url,
            "completedAt": time.time()
        })
        
        log(video_id, "Procesamiento completado exitosamente")
        
        # Limpiar archivos temporales (opcional)
        # shutil.rmtree(TEMP_DIR / video_id)
        
    except Exception as e:
        log(video_id, f"Error: {str(e)}")
        update_job_status(video_id, "failed", {
            "error": str(e),
            "failedAt": time.time()
        })
        raise


def main():
    """Loop principal del worker"""
    log("WORKER", "Worker iniciado, esperando trabajos...")
    
    while True:
        try:
            # Obtener trabajo de la cola (blocking)
            result = redis_client.brpop("video:queue", timeout=5)
            
            if result:
                _, video_id = result
                video_id = video_id.decode('utf-8')
                
                # Obtener datos del job
                job_data = redis_client.get(f"job:{video_id}")
                if not job_data:
                    log(video_id, "Job no encontrado en Redis")
                    continue
                
                job = json.loads(job_data)
                data = job["data"]
                
                # Procesar video
                process_video(video_id, data)
                
        except KeyboardInterrupt:
            log("WORKER", "Worker detenido por usuario")
            break
        except Exception as e:
            log("WORKER", f"Error en loop principal: {str(e)}")
            time.sleep(5)


if __name__ == "__main__":
    main()

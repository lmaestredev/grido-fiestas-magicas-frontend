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
import signal
import sys
from pathlib import Path
import redis
import boto3
from typing import Dict, Any
import requests

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configurar logging estructurado
from utils.logging_structured import setup_structured_logging
use_json_logging = os.getenv("USE_JSON_LOGGING", "false").lower() == "true"
setup_structured_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    use_json=use_json_logging
)
logger = logging.getLogger(__name__)

# Flag para graceful shutdown
shutdown_requested = False
current_job_id = None

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

# Importar configuración de Papá Noel
from papa_noel_config import (
    generate_frame2_script,
    generate_frame3_script,
    get_papa_noel_voice_id,
    get_papa_noel_avatar_id,
)

# Mantener compatibilidad con código existente
FRAME2_PHRASE = generate_frame2_script()

def get_frame3_template():
    """Obtiene la plantilla del Frame 3 (usada para compatibilidad)."""
    # Esta función se usa para generar el script con form_data
    pass


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
    Sube el video usando el storage provider configurado.
    
    Args:
        video_id: ID del video
        file_path: Path al archivo a subir
    
    Returns:
        URL pública del video
    """
    from storage import upload_video
    return upload_video(video_id, file_path)


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


def validate_assets():
    """Valida que todos los assets estén disponibles."""
    from utils.validation import validate_asset_path, validate_video_file
    
    required_assets = [
        "Frames_1_2_to_3.mov",
        "frame3_santa_base.mp4",
        "Frame_4_NocheMagica.mov"
    ]
    
    for asset_name in required_assets:
        asset_path = ASSETS_PATH / asset_name
        if not validate_asset_path(asset_path):
            raise Exception(f"Asset no válido o no encontrado: {asset_name}")
        
        is_valid, error = validate_video_file(asset_path)
        if not is_valid:
            raise Exception(f"Asset inválido {asset_name}: {error}")


def signal_handler(signum, frame):
    """Maneja señales de terminación para graceful shutdown."""
    global shutdown_requested, current_job_id
    logger.info(f"Señal {signum} recibida. Iniciando graceful shutdown...")
    shutdown_requested = True
    if current_job_id:
        logger.info(f"Terminando trabajo actual: {current_job_id}")


# Registrar signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def process_video(video_id: str, data: Dict[str, Any]):
    """
    Procesa un video completo.
    
    Args:
        video_id: ID del video
        data: Datos del formulario
    """
    global current_job_id
    current_job_id = video_id
    
    # Usar job locking para evitar procesamiento duplicado
    from utils.job_locking import acquire_job_lock
    
    try:
        with acquire_job_lock(redis_client, video_id, timeout=1800, blocking=False):
            log(video_id, "Iniciando procesamiento...")
            update_job_status(video_id, "processing")
            
            # Verificar si se solicitó shutdown
            if shutdown_requested:
                log(video_id, "Shutdown solicitado, cancelando procesamiento")
                update_job_status(video_id, "cancelled", {
                    "reason": "Graceful shutdown",
                    "cancelledAt": time.time()
                })
                return
            
            _process_video_internal(video_id, data)
            
    except Exception as e:
        # Si no se pudo adquirir el lock, el trabajo ya está siendo procesado
        if "No se pudo adquirir lock" in str(e):
            log(video_id, "Trabajo ya está siendo procesado por otro worker")
            return
        
        # Otro error, agregar a DLQ
        log(video_id, f"Error procesando video: {str(e)}")
        _handle_video_failure(video_id, data, str(e))
        raise
    finally:
        current_job_id = None


def _process_video_internal(video_id: str, data: Dict[str, Any]):
    """Procesamiento interno del video (sin locking)."""
    from utils.metrics import get_metrics_collector
    
    metrics = get_metrics_collector()
    start_time = metrics.record_job_start(video_id)
    strategy_used = "unknown"
    
    try:
        log(video_id, "Iniciando procesamiento interno...")
        
        # Validar assets al inicio
        try:
            validate_assets()
            log(video_id, "Assets validados correctamente")
        except Exception as e:
            log(video_id, f"Error validando assets: {str(e)}")
            raise
        
        # Validar datos del formulario
        from utils.validation import validate_form_data
        is_valid, errors = validate_form_data(data)
        if not is_valid:
            error_msg = "; ".join(errors)
            log(video_id, f"Error validando datos: {error_msg}")
            raise Exception(f"Datos inválidos: {error_msg}")
        
        # Crear directorio temporal
        temp_dir = TEMP_DIR / video_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Import ProviderManager
        from providers.manager import ProviderManager
        
        # Initialize provider manager
        manager = ProviderManager()
        
        # Prepare script for frame 3 usando configuración de Papá Noel
        script_frame3 = generate_frame3_script(data)
        
        # Paths to assets (usando videos .mov para mantener transparencia)
        intro_base = ASSETS_PATH / "Frames_1_2_to_3.mov"
        frame3_base = ASSETS_PATH / "frame3_santa_base.mp4"  # Solo usado en Strategy 1 (lip-sync)
        outro = ASSETS_PATH / "Frame_4_NocheMagica.mov"
        
        # Final video path
        final_video = temp_dir / "video_final.mp4"
        
        # Trackear qué estrategia se usa (se actualizará en process_video_with_fallback)
        tts_start = time.time()
        
        # Use ProviderManager to process video with fallback
        # Usar configuración de Papá Noel para voice_id y avatar_id
        manager.process_video_with_fallback(
            intro_video=intro_base,
            base_video=frame3_base,
            outro_video=outro,
            script_frame2=generate_frame2_script(),
            script_frame3=script_frame3,
            output_path=final_video,
            video_id=video_id,
            voice_id=get_papa_noel_voice_id(),
            avatar_id=get_papa_noel_avatar_id(),
        )
        
        tts_time = time.time() - tts_start
        metrics.record_timing("composition", tts_time)
        
        # PASO 6: Subir video (Firebase/Vercel/Railway/S3/R2/Local según STORAGE_TYPE)
        storage_start = time.time()
        from storage import upload_video
        video_url = upload_video(video_id, final_video)
        storage_time = time.time() - storage_start
        metrics.record_timing("storage", storage_time)
        
        # PASO 7: Enviar email
        send_email(video_id, data["email"], data["nombre"], video_url)
        
        # Actualizar estado
        update_job_status(video_id, "completed", {
            "videoUrl": video_url,
            "completedAt": time.time()
        })
        
        log(video_id, "Procesamiento completado exitosamente")
        
        # Registrar métricas
        metrics.record_job_complete(video_id, start_time, strategy_used)
        
        # Limpiar archivos temporales (opcional)
        # shutil.rmtree(TEMP_DIR / video_id)
        
    except Exception as e:
        log(video_id, f"Error: {str(e)}")
        metrics.record_job_failed(video_id, start_time)
        _handle_video_failure(video_id, data, str(e))
        raise


def _handle_video_failure(video_id: str, data: Dict[str, Any], error: str):
    """Maneja fallos en el procesamiento de video."""
    from utils.dlq import DeadLetterQueue
    
    # Obtener número de intentos
    job_data = redis_client.get(f"job:{video_id}")
    if job_data:
        if isinstance(job_data, bytes):
            job_data = job_data.decode("utf-8")
        job = json.loads(job_data)
        attempt = job.get("attempt", 1)
        max_attempts = int(os.getenv("MAX_JOB_ATTEMPTS", "3"))
    else:
        attempt = 1
        max_attempts = int(os.getenv("MAX_JOB_ATTEMPTS", "3"))
    
    # Actualizar estado
    update_job_status(video_id, "failed", {
        "error": error,
        "failedAt": time.time(),
        "attempt": attempt
    })
    
    # Si excedió intentos máximos, agregar a DLQ
    if attempt >= max_attempts:
        dlq = DeadLetterQueue(redis_client)
        dlq.add(video_id, data, error, attempt, max_attempts)
        log(video_id, f"Trabajo agregado a DLQ después de {attempt} intentos")
    else:
        # Reintentar
        attempt += 1
        job_data = {
            "videoId": video_id,
            "status": "pending",
            "data": data,
            "attempt": attempt,
            "max_attempts": max_attempts
        }
        redis_client.set(f"job:{video_id}", json.dumps(job_data))
        redis_client.lpush("video:queue", video_id)
        log(video_id, f"Reintentando trabajo (intento {attempt}/{max_attempts})")


def main():
    """Loop principal del worker con graceful shutdown."""
    global shutdown_requested
    
    log("WORKER", "Worker iniciado, esperando trabajos...")
    
    # Health check inicial
    try:
        from health_check import health_check
        health = health_check()
        if health["status"] != "healthy":
            logger.warning(f"Health check inicial falló: {health}")
    except Exception as e:
        logger.warning(f"Error en health check inicial: {e}")
    
    while not shutdown_requested:
        try:
            # Obtener trabajo de la cola (blocking con timeout para permitir verificar shutdown)
            result = redis_client.brpop("video:queue", timeout=5)
            
            if result:
                _, video_id = result
                video_id = video_id.decode('utf-8')
                
                # Verificar shutdown antes de procesar
                if shutdown_requested:
                    log("WORKER", "Shutdown solicitado, no procesando nuevos trabajos")
                    # Devolver trabajo a la cola
                    redis_client.lpush("video:queue", video_id)
                    break
                
                # Obtener datos del job
                job_data = redis_client.get(f"job:{video_id}")
                if not job_data:
                    log(video_id, "Job no encontrado en Redis")
                    continue
                
                # Decodificar si es bytes
                if isinstance(job_data, bytes):
                    job_data = job_data.decode('utf-8')
                
                job = json.loads(job_data)
                data = job.get("data", {})
                
                # Si data está vacío, intentar usar el job completo como data
                if not data:
                    data = job
                
                # Procesar video
                process_video(video_id, data)
                
        except KeyboardInterrupt:
            log("WORKER", "Worker detenido por usuario (Ctrl+C)")
            shutdown_requested = True
            break
        except Exception as e:
            log("WORKER", f"Error en loop principal: {str(e)}")
            if not shutdown_requested:
                time.sleep(5)
    
    # Graceful shutdown: esperar a que termine el trabajo actual
    if current_job_id:
        log("WORKER", f"Esperando a que termine el trabajo actual: {current_job_id}")
        timeout = 300  # 5 minutos máximo
        start_time = time.time()
        while current_job_id and (time.time() - start_time) < timeout:
            time.sleep(1)
        if current_job_id:
            log("WORKER", f"Timeout esperando trabajo {current_job_id}")
    
    log("WORKER", "Worker detenido correctamente")


if __name__ == "__main__":
    main()

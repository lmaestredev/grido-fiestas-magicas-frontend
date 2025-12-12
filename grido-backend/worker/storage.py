"""
Storage providers para subir videos generados.
Soporta múltiples opciones: Firebase Storage, Vercel Blob, Railway, S3/R2, o local.
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Optional

# Third-party imports (condicionales - se importan cuando se necesitan)
# firebase_admin - importado en upload_to_firebase()
# vercel_blob - importado en upload_to_vercel_blob()
# boto3 - importado en upload_to_s3_r2()

logger = logging.getLogger(__name__)


# ============================================================================
# Environment Variables Configuration
# ============================================================================
# Variables de entorno utilizadas:
#
# General:
#   STORAGE_TYPE: Tipo de storage a usar (firebase, vercel, railway, s3, r2, local)
#
# Firebase:
#   FIREBASE_STORAGE_BUCKET: Nombre del bucket de Firebase Storage
#   FIREBASE_CREDENTIALS_PATH: Ruta al archivo JSON de credenciales
#   FIREBASE_CREDENTIALS_JSON: Contenido JSON de credenciales como string
#
# Vercel Blob:
#   VERCEL_BLOB_TOKEN: Token de autenticación de Vercel Blob
#
# Railway:
#   RAILWAY_STORAGE_PATH: Ruta donde guardar videos en Railway
#   API_BASE_URL: URL base de la API para servir videos
#
# S3/R2:
#   AWS_ENDPOINT_URL: Endpoint URL (requerido para R2)
#   AWS_ACCESS_KEY_ID: Access key ID
#   AWS_SECRET_ACCESS_KEY: Secret access key
#   S3_BUCKET: Nombre del bucket
#   AWS_REGION: Región de AWS (default: us-east-1)
#
# Local:
#   LOCAL_STORAGE_PATH: Ruta donde guardar videos localmente (default: ./storage)
# ============================================================================


def upload_video(video_id: str, file_path: Path) -> str:
    """
    Sube un video usando el storage provider configurado.
    
    Args:
        video_id: ID del video
        file_path: Path al archivo de video
        
    Returns:
        URL pública del video
        
    Raises:
        Exception: Si el upload falla
    """
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "firebase":
        return upload_to_firebase(video_id, file_path)
    elif storage_type == "vercel":
        return upload_to_vercel_blob(video_id, file_path)
    elif storage_type == "railway":
        return upload_to_railway(video_id, file_path)
    elif storage_type in ("s3", "r2"):
        return upload_to_s3_r2(video_id, file_path)
    else:
        return save_local(video_id, file_path)


def upload_to_firebase(video_id: str, file_path: Path) -> str:
    """Sube video a Firebase Storage."""
    try:
        import firebase_admin
        from firebase_admin import credentials, storage
    except ImportError:
        raise Exception("firebase-admin no está instalado. Instala con: pip install firebase-admin")
    
    logger.info(f"[{video_id}] Subiendo a Firebase Storage...")
    
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")
    if not storage_bucket:
        raise Exception("FIREBASE_STORAGE_BUCKET no configurado")
    
    # Inicializar Firebase si no está inicializado
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        
        # Intentar usar credenciales explícitas primero
        if cred_path and Path(cred_path).exists():
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket
            })
        elif cred_json:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket
            })
        else:
            # Intentar usar Application Default Credentials (ADC)
            try:
                firebase_admin.initialize_app(options={
                    'storageBucket': storage_bucket
                })
                logger.info(f"[{video_id}] Usando Application Default Credentials")
            except Exception as adc_error:
                raise Exception(
                    "No se encontraron credenciales de Firebase. Opciones:\n"
                    "1. Configura FIREBASE_CREDENTIALS_PATH con ruta al archivo JSON\n"
                    "2. Configura FIREBASE_CREDENTIALS_JSON con el contenido JSON\n"
                    "3. Usa 'gcloud auth application-default login' para ADC\n"
                    "4. Crea una nueva Service Account en Google Cloud Console → IAM & Admin → Service Accounts"
                ) from adc_error
    
    bucket = storage.bucket(storage_bucket)
    blob_path = f"videos/{video_id}.mp4"
    blob = bucket.blob(blob_path)
    
    blob.metadata = {
        'contentType': 'video/mp4',
        'cacheControl': 'public, max-age=31536000'
    }
    
    blob.upload_from_filename(str(file_path), content_type="video/mp4")
    blob.make_public()
    video_url = blob.public_url
    
    logger.info(f"[{video_id}] Video subido a Firebase: {video_url}")
    return video_url


def upload_to_vercel_blob(video_id: str, file_path: Path) -> str:
    """Sube video a Vercel Blob Storage."""
    try:
        from vercel_blob import put
    except ImportError:
        raise Exception("vercel-blob no está instalado. Instala con: pip install vercel-blob")
    
    logger.info(f"[{video_id}] Subiendo a Vercel Blob...")
    
    token = os.getenv("VERCEL_BLOB_TOKEN")
    if not token:
        raise Exception("VERCEL_BLOB_TOKEN no configurado")
    
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    blob_path = f"videos/{video_id}.mp4"
    result = put(
        blob_path,
        file_data,
        access="public",
        token=token,
        content_type="video/mp4"
    )
    
    video_url = result.url
    logger.info(f"[{video_id}] Video subido a Vercel Blob: {video_url}")
    return video_url


def upload_to_railway(video_id: str, file_path: Path) -> str:
    """
    Railway no tiene un servicio de storage dedicado.
    Esta función guarda el video localmente y retorna una URL que apunta
    a un endpoint de la API que sirve el video.
    
    Nota: Requiere que tengas un endpoint en tu API para servir videos.
    """
    logger.info(f"[{video_id}] Guardando video para Railway...")
    
    storage_path = Path(os.getenv("RAILWAY_STORAGE_PATH", "/app/storage"))
    storage_path.mkdir(parents=True, exist_ok=True)
    
    destination = storage_path / f"{video_id}.mp4"
    shutil.copy2(file_path, destination)
    
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:3000")
    video_url = f"{api_base_url}/api/videos/{video_id}.mp4"
    
    logger.info(f"[{video_id}] Video guardado en Railway: {video_url}")
    return video_url


def upload_to_s3_r2(video_id: str, file_path: Path) -> str:
    """Sube video a S3 o R2 (Cloudflare)."""
    import boto3
    
    logger.info(f"[{video_id}] Subiendo a S3/R2...")
    
    endpoint_url = os.getenv("AWS_ENDPOINT_URL")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket = os.getenv("S3_BUCKET")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    if not all([access_key, secret_key, bucket]):
        raise Exception("Credenciales de S3/R2 no configuradas")
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region if not endpoint_url else 'auto'
    )
    
    key = f"videos/{video_id}.mp4"
    
    s3_client.upload_file(
        str(file_path),
        bucket,
        key,
        ExtraArgs={'ContentType': 'video/mp4'}
    )
    
    if endpoint_url:  # R2
        video_url = f"https://{bucket}.r2.dev/{key}"
    else:  # S3
        video_url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    
    logger.info(f"[{video_id}] Video subido: {video_url}")
    return video_url


def save_local(video_id: str, file_path: Path) -> str:
    """
    Guarda el video localmente (para pruebas).
    Retorna una ruta local que puede ser servida por un servidor local.
    """
    logger.info(f"[{video_id}] Guardando video localmente...")
    
    local_storage = Path(os.getenv("LOCAL_STORAGE_PATH", "./storage"))
    local_storage.mkdir(parents=True, exist_ok=True)
    
    destination = local_storage / f"{video_id}.mp4"
    shutil.copy2(file_path, destination)
    
    video_url = f"file://{destination.absolute()}"
    
    logger.info(f"[{video_id}] Video guardado localmente: {destination}")
    logger.info(f"[{video_id}] Para servir: python -m http.server 8000 --directory {local_storage}")
    
    return video_url

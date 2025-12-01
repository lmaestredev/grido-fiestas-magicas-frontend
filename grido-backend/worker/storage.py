"""
Storage providers para subir videos generados.
Soporta múltiples opciones: Firebase Storage, Vercel Blob, Railway, S3/R2, o local.
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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
    elif storage_type == "s3" or storage_type == "r2":
        return upload_to_s3_r2(video_id, file_path)
    else:
        # Default: local storage (para pruebas)
        return save_local(video_id, file_path)


def upload_to_firebase(video_id: str, file_path: Path) -> str:
    """Sube video a Firebase Storage."""
    try:
        import firebase_admin
        from firebase_admin import credentials, storage
    except ImportError:
        raise Exception("firebase-admin no está instalado. Instala con: pip install firebase-admin")
    
    logger.info(f"[{video_id}] Subiendo a Firebase Storage...")
    
    # Obtener storage bucket (puede venir de config o variable de entorno)
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET", "grido-479823.firebasestorage.app")
    
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
            # Usar credenciales desde variable de entorno (JSON string)
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket
            })
        else:
            # Intentar usar Application Default Credentials (ADC)
            # Útil cuando se ejecuta en Google Cloud o con gcloud auth
            try:
                # ADC se detecta automáticamente si está configurado
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
    
    # Configurar metadata
    blob.metadata = {
        'contentType': 'video/mp4',
        'cacheControl': 'public, max-age=31536000'
    }
    
    # Subir archivo
    blob.upload_from_filename(str(file_path), content_type="video/mp4")
    
    # Hacer público y obtener URL
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
    
    # Leer archivo
    with open(file_path, "rb") as f:
        file_data = f.read()
    
    # Subir a Vercel Blob
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
    
    # En Railway, normalmente guardarías en un volumen persistente
    # y servirías a través de tu API
    storage_path = Path(os.getenv("RAILWAY_STORAGE_PATH", "/app/storage"))
    storage_path.mkdir(parents=True, exist_ok=True)
    
    destination = storage_path / f"{video_id}.mp4"
    import shutil
    shutil.copy2(file_path, destination)
    
    # URL que apunta a tu API (ajustar según tu dominio)
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:3000")
    video_url = f"{api_base_url}/api/videos/{video_id}.mp4"
    
    logger.info(f"[{video_id}] Video guardado en Railway: {video_url}")
    return video_url


def upload_to_s3_r2(video_id: str, file_path: Path) -> str:
    """Sube video a S3 o R2 (Cloudflare)."""
    import boto3
    
    logger.info(f"[{video_id}] Subiendo a S3/R2...")
    
    # Configuración
    endpoint_url = os.getenv("AWS_ENDPOINT_URL")  # Para R2
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket = os.getenv("S3_BUCKET")
    region = os.getenv("AWS_REGION", "us-east-1")
    
    if not all([access_key, secret_key, bucket]):
        raise Exception("Credenciales de S3/R2 no configuradas")
    
    # Crear cliente
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region if not endpoint_url else 'auto'
    )
    
    key = f"videos/{video_id}.mp4"
    
    # Subir archivo
    s3_client.upload_file(
        str(file_path),
        bucket,
        key,
        ExtraArgs={'ContentType': 'video/mp4'}
    )
    
    # Generar URL
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
    
    # Directorio de storage local
    local_storage = Path(os.getenv("LOCAL_STORAGE_PATH", "./storage"))
    local_storage.mkdir(parents=True, exist_ok=True)
    
    destination = local_storage / f"{video_id}.mp4"
    import shutil
    shutil.copy2(file_path, destination)
    
    # URL local (para pruebas)
    video_url = f"file://{destination.absolute()}"
    
    logger.info(f"[{video_id}] Video guardado localmente: {destination}")
    logger.info(f"[{video_id}] Para servir: python -m http.server 8000 --directory {local_storage}")
    
    return video_url


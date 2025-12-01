"""
Utilidades para limpieza automática de archivos temporales.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def cleanup_temp_files(
    temp_dir: Path,
    max_age_hours: int = 24,
    dry_run: bool = False
) -> dict:
    """
    Limpia archivos temporales más antiguos que max_age_hours.
    
    Args:
        temp_dir: Directorio temporal a limpiar
        max_age_hours: Edad máxima en horas
        dry_run: Si True, solo muestra qué se eliminaría sin eliminar
        
    Returns:
        Dict con estadísticas de limpieza
    """
    if not temp_dir.exists():
        return {"deleted": 0, "size_freed_mb": 0, "errors": 0}
    
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    deleted = 0
    size_freed = 0
    errors = 0
    
    for item in temp_dir.rglob("*"):
        try:
            if item.is_file():
                age = current_time - item.stat().st_mtime
                if age > max_age_seconds:
                    size = item.stat().st_size
                    if not dry_run:
                        item.unlink()
                    deleted += 1
                    size_freed += size
                    logger.debug(f"{'Would delete' if dry_run else 'Deleted'}: {item} ({age/3600:.1f}h old)")
        except Exception as e:
            errors += 1
            logger.warning(f"Error procesando {item}: {e}")
    
    size_freed_mb = size_freed / (1024 * 1024)
    
    if not dry_run:
        logger.info(
            f"Limpieza completada: {deleted} archivos eliminados, "
            f"{size_freed_mb:.2f}MB liberados, {errors} errores"
        )
    else:
        logger.info(
            f"Dry run: {deleted} archivos serían eliminados, "
            f"{size_freed_mb:.2f}MB serían liberados"
        )
    
    return {
        "deleted": deleted,
        "size_freed_mb": size_freed_mb,
        "errors": errors
    }


def cleanup_old_jobs(
    redis_client,
    max_age_hours: int = 168,  # 7 días por defecto
    dry_run: bool = False
) -> dict:
    """
    Limpia trabajos antiguos de Redis.
    
    Args:
        redis_client: Cliente de Redis
        max_age_hours: Edad máxima en horas
        dry_run: Si True, solo muestra qué se eliminaría
        
    Returns:
        Dict con estadísticas de limpieza
    """
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    deleted = 0
    
    # Buscar todos los jobs
    keys = redis_client.keys("job:*")
    
    for key in keys:
        try:
            job_data = redis_client.get(key)
            if not job_data:
                continue
            
            if isinstance(job_data, bytes):
                job_data = job_data.decode("utf-8")
            
            import json
            job = json.loads(job_data)
            
            # Verificar edad
            created_at = job.get("createdAt")
            if created_at:
                # Convertir timestamp ISO a timestamp
                from datetime import datetime
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    created_timestamp = dt.timestamp()
                else:
                    created_timestamp = created_at
                
                age = current_time - created_timestamp
                if age > max_age_seconds:
                    status = job.get("status", "unknown")
                    # Solo eliminar trabajos completados o fallidos antiguos
                    if status in ["completed", "failed", "cancelled"]:
                        if not dry_run:
                            redis_client.delete(key)
                        deleted += 1
                        logger.debug(
                            f"{'Would delete' if dry_run else 'Deleted'} job: {key} "
                            f"(status: {status}, age: {age/3600:.1f}h)"
                        )
        except Exception as e:
            logger.warning(f"Error procesando job {key}: {e}")
    
    if not dry_run:
        logger.info(f"Limpieza de jobs completada: {deleted} jobs eliminados")
    else:
        logger.info(f"Dry run: {deleted} jobs serían eliminados")
    
    return {"deleted": deleted}


def schedule_cleanup(
    temp_dir: Path,
    redis_client,
    interval_hours: int = 6,
    temp_max_age_hours: int = 24,
    jobs_max_age_hours: int = 168
):
    """
    Programa limpieza automática periódica.
    
    Args:
        temp_dir: Directorio temporal a limpiar
        redis_client: Cliente de Redis
        interval_hours: Intervalo entre limpiezas en horas
        temp_max_age_hours: Edad máxima de archivos temporales
        jobs_max_age_hours: Edad máxima de jobs en Redis
    """
    import threading
    
    def cleanup_loop():
        while True:
            time.sleep(interval_hours * 3600)
            logger.info("Iniciando limpieza automática...")
            cleanup_temp_files(temp_dir, temp_max_age_hours)
            cleanup_old_jobs(redis_client, jobs_max_age_hours)
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info(f"Limpieza automática programada cada {interval_hours} horas")


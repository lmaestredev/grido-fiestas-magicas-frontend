"""
Dead Letter Queue (DLQ) para trabajos fallidos.
"""

import json
import time
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DeadLetterQueue:
    """Cola de trabajos fallidos que requieren revisión manual."""
    
    def __init__(self, redis_client, dlq_key: str = "dlq:video:failed"):
        """
        Inicializa la Dead Letter Queue.
        
        Args:
            redis_client: Cliente de Redis
            dlq_key: Clave de Redis para la DLQ
        """
        self.redis_client = redis_client
        self.dlq_key = dlq_key
    
    def add(
        self,
        video_id: str,
        data: Dict[str, Any],
        error: str,
        attempt: int = 1,
        max_attempts: int = 3
    ):
        """
        Agrega un trabajo fallido a la DLQ.
        
        Args:
            video_id: ID del video
            data: Datos del formulario
            error: Mensaje de error
            attempt: Número de intento actual
            max_attempts: Número máximo de intentos
        """
        dlq_entry = {
            "video_id": video_id,
            "data": data,
            "error": error,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "failed_at": time.time(),
            "failed_at_iso": __import__("datetime").datetime.utcnow().isoformat() + "Z"
        }
        
        # Guardar en Redis como hash
        self.redis_client.hset(
            f"{self.dlq_key}:{video_id}",
            mapping={
                "entry": json.dumps(dlq_entry),
                "failed_at": str(time.time())
            }
        )
        
        # Agregar a lista de IDs fallidos
        self.redis_client.lpush(f"{self.dlq_key}:ids", video_id)
        
        logger.error(f"Trabajo {video_id} agregado a DLQ: {error}")
    
    def get(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un trabajo de la DLQ.
        
        Args:
            video_id: ID del video
            
        Returns:
            Entrada de la DLQ o None si no existe
        """
        entry_data = self.redis_client.hget(f"{self.dlq_key}:{video_id}", "entry")
        if entry_data:
            if isinstance(entry_data, bytes):
                entry_data = entry_data.decode("utf-8")
            return json.loads(entry_data)
        return None
    
    def list_all(self, limit: int = 100) -> list:
        """
        Lista todos los trabajos en la DLQ.
        
        Args:
            limit: Número máximo de trabajos a retornar
            
        Returns:
            Lista de entradas de la DLQ
        """
        ids = self.redis_client.lrange(f"{self.dlq_key}:ids", 0, limit - 1)
        entries = []
        
        for video_id_bytes in ids:
            video_id = video_id_bytes.decode("utf-8") if isinstance(video_id_bytes, bytes) else video_id_bytes
            entry = self.get(video_id)
            if entry:
                entries.append(entry)
        
        return entries
    
    def remove(self, video_id: str) -> bool:
        """
        Remueve un trabajo de la DLQ.
        
        Args:
            video_id: ID del video
            
        Returns:
            True si se removió correctamente
        """
        # Remover de la lista de IDs
        self.redis_client.lrem(f"{self.dlq_key}:ids", 0, video_id)
        
        # Remover el hash
        deleted = self.redis_client.delete(f"{self.dlq_key}:{video_id}")
        
        if deleted:
            logger.info(f"Trabajo {video_id} removido de DLQ")
        
        return deleted > 0
    
    def retry(self, video_id: str) -> bool:
        """
        Reintenta un trabajo de la DLQ agregándolo de nuevo a la cola.
        
        Args:
            video_id: ID del video
            
        Returns:
            True si se agregó a la cola correctamente
        """
        entry = self.get(video_id)
        if not entry:
            return False
        
        # Agregar de nuevo a la cola
        self.redis_client.lpush("video:queue", video_id)
        
        # Actualizar job status
        job_data = {
            "videoId": video_id,
            "status": "pending",
            "data": entry["data"],
            "retried_from_dlq": True,
            "retried_at": time.time()
        }
        self.redis_client.set(f"job:{video_id}", json.dumps(job_data))
        
        # Remover de DLQ
        self.remove(video_id)
        
        logger.info(f"Trabajo {video_id} reintentado desde DLQ")
        return True
    
    def count(self) -> int:
        """
        Retorna el número de trabajos en la DLQ.
        
        Returns:
            Número de trabajos en la DLQ
        """
        return self.redis_client.llen(f"{self.dlq_key}:ids")


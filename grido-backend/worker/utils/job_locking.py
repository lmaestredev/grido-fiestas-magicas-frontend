"""
Sistema de locking distribuido para trabajos usando Redis.
"""

import os
import time
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class JobLock:
    """Lock distribuido para trabajos usando Redis."""
    
    def __init__(self, redis_client, job_id: str, timeout: int = 600):
        """
        Inicializa un lock para un trabajo.
        
        Args:
            redis_client: Cliente de Redis
            job_id: ID del trabajo
            timeout: Tiempo máximo de lock en segundos (default: 10 minutos)
        """
        self.redis_client = redis_client
        self.job_id = job_id
        self.lock_key = f"lock:job:{job_id}"
        self.timeout = timeout
        self.lock_value = None
    
    def acquire(self, blocking: bool = True, timeout: float = 5.0) -> bool:
        """
        Adquiere el lock.
        
        Args:
            blocking: Si True, espera hasta obtener el lock
            timeout: Tiempo máximo de espera en segundos
            
        Returns:
            True si se adquirió el lock, False si no
        """
        import uuid
        self.lock_value = str(uuid.uuid4())
        end_time = time.time() + timeout
        
        while True:
            # Intentar adquirir el lock usando SET con NX (only if not exists)
            acquired = self.redis_client.set(
                self.lock_key,
                self.lock_value,
                nx=True,  # Solo establecer si no existe
                ex=self.timeout  # Expirar después de timeout segundos
            )
            
            if acquired:
                logger.info(f"Lock adquirido para job: {self.job_id}")
                return True
            
            if not blocking or time.time() >= end_time:
                logger.warning(f"No se pudo adquirir lock para job: {self.job_id}")
                return False
            
            # Esperar un poco antes de reintentar
            time.sleep(0.1)
    
    def release(self) -> bool:
        """
        Libera el lock.
        
        Returns:
            True si se liberó correctamente
        """
        if not self.lock_value:
            return False
        
        # Script Lua para liberar el lock de forma atómica
        # Solo libera si el valor coincide (para evitar liberar el lock de otro proceso)
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            result = self.redis_client.eval(
                lua_script,
                1,
                self.lock_key,
                self.lock_value
            )
            
            if result:
                logger.info(f"Lock liberado para job: {self.job_id}")
                return True
            else:
                logger.warning(f"No se pudo liberar lock para job: {self.job_id} (valor no coincide)")
                return False
        except Exception as e:
            logger.error(f"Error liberando lock: {e}")
            return False
    
    def extend(self, additional_time: int = 300) -> bool:
        """
        Extiende el tiempo del lock.
        
        Args:
            additional_time: Tiempo adicional en segundos
            
        Returns:
            True si se extendió correctamente
        """
        if not self.lock_value:
            return False
        
        # Script Lua para extender el lock de forma atómica
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        
        try:
            result = self.redis_client.eval(
                lua_script,
                1,
                self.lock_key,
                self.lock_value,
                additional_time
            )
            
            if result:
                logger.debug(f"Lock extendido para job: {self.job_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error extendiendo lock: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        if not self.acquire():
            raise Exception(f"No se pudo adquirir lock para job: {self.job_id}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


@contextmanager
def acquire_job_lock(redis_client, job_id: str, timeout: int = 600, blocking: bool = True):
    """
    Context manager para adquirir un lock de trabajo.
    
    Args:
        redis_client: Cliente de Redis
        job_id: ID del trabajo
        timeout: Tiempo máximo de lock en segundos
        blocking: Si True, espera hasta obtener el lock
        
    Yields:
        JobLock instance
        
    Raises:
        Exception: Si no se pudo adquirir el lock
    """
    lock = JobLock(redis_client, job_id, timeout)
    try:
        if not lock.acquire(blocking=blocking):
            raise Exception(f"No se pudo adquirir lock para job: {job_id}")
        yield lock
    finally:
        lock.release()


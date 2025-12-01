"""
Retry logic con exponential backoff.
"""

import time
import logging
from typing import Callable, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorador para retry con exponential backoff.
    
    Args:
        max_retries: Número máximo de reintentos
        base_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        exponential_base: Base para el exponential backoff
        exceptions: Tupla de excepciones a capturar
        on_retry: Callback llamado en cada retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        # Último intento, lanzar excepción
                        logger.error(
                            f"{func.__name__} failed after {max_retries} attempts: {str(e)}"
                        )
                        raise
                    
                    # Calcular delay con exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    time.sleep(delay)
            
            # No debería llegar aquí, pero por si acaso
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def retry_function(
    func: Callable[..., T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> T:
    """
    Ejecuta una función con retry logic.
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        exponential_base: Base para el exponential backoff
        exceptions: Tupla de excepciones a capturar
        *args, **kwargs: Argumentos para la función
        
    Returns:
        Resultado de la función
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries - 1:
                logger.error(
                    f"{func.__name__} failed after {max_retries} attempts: {str(e)}"
                )
                raise
            
            delay = min(
                base_delay * (exponential_base ** attempt),
                max_delay
            )
            
            logger.warning(
                f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            time.sleep(delay)
    
    if last_exception:
        raise last_exception


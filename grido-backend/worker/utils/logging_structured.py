"""
Logging estructurado en formato JSON.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class StructuredJSONFormatter(logging.Formatter):
    """Formatter que produce logs en formato JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea un log record como JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar video_id si está presente
        if hasattr(record, "video_id"):
            log_data["video_id"] = record.video_id
        
        # Agregar contexto adicional si está presente
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Agregar excepciones si están presentes
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar stack trace si está en modo debug
        if record.levelno == logging.DEBUG and hasattr(record, "stack_info"):
            log_data["stack"] = record.stack_info
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_structured_logging(
    level: str = "INFO",
    output_file: Optional[Path] = None,
    use_json: bool = True
) -> logging.Logger:
    """
    Configura logging estructurado.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        output_file: Archivo opcional para escribir logs
        use_json: Si True, usa formato JSON, si False, formato legible
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remover handlers existentes
    logger.handlers.clear()
    
    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(getattr(logging, level.upper()))
    
    if use_json:
        stdout_handler.setFormatter(StructuredJSONFormatter())
    else:
        # Formato que maneja video_id opcional
        class VideoIdFormatter(logging.Formatter):
            def format(self, record):
                if not hasattr(record, 'video_id'):
                    record.video_id = 'N/A'
                return super().format(record)
        
        stdout_handler.setFormatter(
            VideoIdFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(video_id)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
    
    logger.addHandler(stdout_handler)
    
    # Handler para archivo si se especifica
    if output_file:
        file_handler = logging.FileHandler(output_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        if use_json:
            file_handler.setFormatter(StructuredJSONFormatter())
        else:
            # Formato que maneja video_id opcional
            class VideoIdFormatter(logging.Formatter):
                def format(self, record):
                    if not hasattr(record, 'video_id'):
                        record.video_id = 'N/A'
                    return super().format(record)
            
            file_handler.setFormatter(
                VideoIdFormatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(video_id)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str, video_id: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger con contexto de video_id.
    
    Args:
        name: Nombre del logger
        video_id: ID del video (opcional)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Agregar video_id al contexto si está presente
    if video_id:
        old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.video_id = video_id
            return record
        
        logging.setLogRecordFactory(record_factory)
    
    return logger


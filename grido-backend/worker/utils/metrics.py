"""
Sistema básico de métricas para tracking de performance.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Colector simple de métricas."""
    
    def __init__(self):
        """Inicializa el colector de métricas."""
        self.metrics = {
            "jobs_processed": 0,
            "jobs_failed": 0,
            "jobs_completed": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0,
            "tts_time": 0.0,
            "lipsync_time": 0.0,
            "video_composition_time": 0.0,
            "storage_time": 0.0,
            "provider_usage": {},  # {provider_name: count}
            "strategy_usage": {},  # {strategy: count}
        }
    
    def record_job_start(self, video_id: str) -> float:
        """
        Registra el inicio de un trabajo.
        
        Returns:
            Timestamp de inicio
        """
        return time.time()
    
    def record_job_complete(self, video_id: str, start_time: float, strategy: str = "unknown"):
        """
        Registra la finalización exitosa de un trabajo.
        
        Args:
            video_id: ID del video
            start_time: Timestamp de inicio
            strategy: Estrategia usada
        """
        processing_time = time.time() - start_time
        
        self.metrics["jobs_processed"] += 1
        self.metrics["jobs_completed"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["avg_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["jobs_processed"]
        )
        
        # Trackear estrategia
        self.metrics["strategy_usage"][strategy] = (
            self.metrics["strategy_usage"].get(strategy, 0) + 1
        )
        
        logger.info(
            f"[{video_id}] Métricas: tiempo={processing_time:.2f}s, "
            f"estrategia={strategy}, promedio={self.metrics['avg_processing_time']:.2f}s"
        )
    
    def record_job_failed(self, video_id: str, start_time: float):
        """
        Registra el fallo de un trabajo.
        
        Args:
            video_id: ID del video
            start_time: Timestamp de inicio
        """
        processing_time = time.time() - start_time
        
        self.metrics["jobs_processed"] += 1
        self.metrics["jobs_failed"] += 1
        self.metrics["total_processing_time"] += processing_time
        self.metrics["avg_processing_time"] = (
            self.metrics["total_processing_time"] / self.metrics["jobs_processed"]
        )
    
    def record_provider_usage(self, provider_name: str, success: bool = True):
        """
        Registra el uso de un provider.
        
        Args:
            provider_name: Nombre del provider
            success: Si fue exitoso
        """
        key = f"{provider_name}_{'success' if success else 'failed'}"
        self.metrics["provider_usage"][key] = (
            self.metrics["provider_usage"].get(key, 0) + 1
        )
    
    def record_timing(self, stage: str, duration: float):
        """
        Registra el tiempo de una etapa.
        
        Args:
            stage: Nombre de la etapa (tts, lipsync, composition, storage)
            duration: Duración en segundos
        """
        if stage in ["tts", "lipsync", "composition", "storage"]:
            self.metrics[f"{stage}_time"] += duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Obtiene todas las métricas.
        
        Returns:
            Dict con todas las métricas
        """
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["jobs_completed"] / self.metrics["jobs_processed"]
                if self.metrics["jobs_processed"] > 0
                else 0.0
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def reset(self):
        """Resetea todas las métricas."""
        self.__init__()


# Instancia global
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Obtiene la instancia global del colector de métricas."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


"""
Sistema de caché para audios generados.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioCache:
    """Caché para audios generados por TTS."""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_size_mb: int = 1000):
        """
        Inicializa el caché de audios.
        
        Args:
            cache_dir: Directorio para el caché (default: ./cache/audio)
            max_size_mb: Tamaño máximo del caché en MB
        """
        self.cache_dir = cache_dir or Path("cache/audio")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_mb = max_size_mb
        self.index_file = self.cache_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> dict:
        """Carga el índice del caché."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando índice de caché: {e}")
                return {}
        return {}
    
    def _save_index(self):
        """Guarda el índice del caché."""
        try:
            with open(self.index_file, "w") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            logger.warning(f"Error guardando índice de caché: {e}")
    
    def _get_cache_key(self, text: str, voice_id: str, provider: str) -> str:
        """
        Genera una clave única para el caché.
        
        Args:
            text: Texto a convertir a audio
            voice_id: ID de la voz
            provider: Nombre del provider
            
        Returns:
            Hash MD5 del contenido
        """
        content = f"{provider}:{voice_id}:{text}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()
    
    def get(self, text: str, voice_id: str, provider: str) -> Optional[Path]:
        """
        Obtiene un audio del caché si existe.
        
        Args:
            text: Texto del audio
            voice_id: ID de la voz
            provider: Nombre del provider
            
        Returns:
            Path al archivo de audio si existe, None si no está en caché
        """
        cache_key = self._get_cache_key(text, voice_id, provider)
        
        if cache_key in self.index:
            cached_file = Path(self.index[cache_key]["path"])
            if cached_file.exists():
                logger.info(f"Cache hit para audio: {cache_key[:8]}...")
                return cached_file
            else:
                # Archivo no existe, remover del índice
                del self.index[cache_key]
                self._save_index()
        
        return None
    
    def put(self, text: str, voice_id: str, provider: str, audio_path: Path) -> Path:
        """
        Guarda un audio en el caché.
        
        Args:
            text: Texto del audio
            voice_id: ID de la voz
            provider: Nombre del provider
            audio_path: Path al archivo de audio generado
            
        Returns:
            Path al archivo en el caché
        """
        cache_key = self._get_cache_key(text, voice_id, provider)
        cached_file = self.cache_dir / f"{cache_key}.wav"
        
        # Copiar archivo al caché
        import shutil
        shutil.copy2(audio_path, cached_file)
        
        # Actualizar índice
        self.index[cache_key] = {
            "path": str(cached_file),
            "text": text[:100],  # Primeros 100 caracteres para referencia
            "voice_id": voice_id,
            "provider": provider,
            "size": cached_file.stat().st_size,
            "created_at": __import__("time").time()
        }
        
        self._save_index()
        
        # Limpiar caché si es necesario
        self._cleanup_if_needed()
        
        logger.info(f"Audio guardado en caché: {cache_key[:8]}...")
        return cached_file
    
    def _cleanup_if_needed(self):
        """Limpia el caché si excede el tamaño máximo."""
        total_size = sum(
            Path(self.index[key]["path"]).stat().st_size
            for key in self.index
            if Path(self.index[key]["path"]).exists()
        )
        
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            logger.info(f"Caché excede tamaño máximo ({total_size / (1024*1024):.2f}MB), limpiando...")
            
            # Ordenar por fecha de creación (más antiguos primero)
            sorted_items = sorted(
                self.index.items(),
                key=lambda x: x[1].get("created_at", 0)
            )
            
            # Eliminar archivos más antiguos hasta estar bajo el límite
            for key, info in sorted_items:
                if total_size <= max_size_bytes * 0.8:  # Dejar 20% de margen
                    break
                
                cached_file = Path(info["path"])
                if cached_file.exists():
                    file_size = cached_file.stat().st_size
                    cached_file.unlink()
                    total_size -= file_size
                    del self.index[key]
            
            self._save_index()
            logger.info(f"Caché limpiado. Tamaño actual: {total_size / (1024*1024):.2f}MB")
    
    def clear(self):
        """Limpia todo el caché."""
        for key, info in list(self.index.items()):
            cached_file = Path(info["path"])
            if cached_file.exists():
                cached_file.unlink()
        
        self.index = {}
        self._save_index()
        logger.info("Caché limpiado completamente")


# Instancia global del caché
_audio_cache: Optional[AudioCache] = None


def get_audio_cache() -> AudioCache:
    """Obtiene la instancia global del caché de audios."""
    global _audio_cache
    if _audio_cache is None:
        cache_dir = Path(os.getenv("AUDIO_CACHE_DIR", "cache/audio"))
        max_size = int(os.getenv("AUDIO_CACHE_MAX_SIZE_MB", "1000"))
        _audio_cache = AudioCache(cache_dir=cache_dir, max_size_mb=max_size)
    return _audio_cache


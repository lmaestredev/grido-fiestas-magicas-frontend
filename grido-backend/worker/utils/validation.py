"""
Validación y sanitización de inputs.
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple


# Límites de validación
MAX_TEXT_LENGTH = 2000
MAX_NOMBRE_LENGTH = 100
MAX_EMAIL_LENGTH = 255
MAX_PROVINCIA_LENGTH = 50


def validate_form_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida los datos del formulario.
    
    Args:
        data: Datos del formulario
        
    Returns:
        Tuple (is_valid, errors)
    """
    errors = []
    
    # Validar nombre
    nombre = data.get("nombre", "").strip()
    if not nombre:
        errors.append("El nombre es requerido")
    elif len(nombre) > MAX_NOMBRE_LENGTH:
        errors.append(f"El nombre no puede tener más de {MAX_NOMBRE_LENGTH} caracteres")
    elif not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
        errors.append("El nombre contiene caracteres inválidos")
    
    # Validar parentesco
    parentesco = data.get("parentesco", "").strip()
    if not parentesco:
        errors.append("El parentesco es requerido")
    elif len(parentesco) > MAX_NOMBRE_LENGTH:
        errors.append(f"El parentesco no puede tener más de {MAX_NOMBRE_LENGTH} caracteres")
    
    # Validar email
    email = data.get("email", "").strip()
    email_domain = data.get("emailDomain", "").strip()
    full_email = f"{email}{email_domain}"
    
    if not email:
        errors.append("El email es requerido")
    elif len(full_email) > MAX_EMAIL_LENGTH:
        errors.append(f"El email no puede tener más de {MAX_EMAIL_LENGTH} caracteres")
    elif not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", full_email):
        errors.append("El formato del email es inválido")
    
    # Validar provincia
    provincia = data.get("provincia", "").strip()
    if not provincia:
        errors.append("La provincia es requerida")
    elif len(provincia) > MAX_PROVINCIA_LENGTH:
        errors.append(f"La provincia no puede tener más de {MAX_PROVINCIA_LENGTH} caracteres")
    
    # Validar textos largos
    text_fields = ["queHizo", "recuerdoEspecial", "pedidoNocheMagica"]
    for field in text_fields:
        text = data.get(field, "").strip()
        if not text:
            errors.append(f"El campo '{field}' es requerido")
        elif len(text) > MAX_TEXT_LENGTH:
            errors.append(f"El campo '{field}' no puede tener más de {MAX_TEXT_LENGTH} caracteres")
    
    return len(errors) == 0, errors


def sanitize_text(text: str) -> str:
    """
    Sanitiza texto removiendo caracteres peligrosos.
    
    Args:
        text: Texto a sanitizar
        
    Returns:
        Texto sanitizado
    """
    # Remover caracteres de control excepto newlines y tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', text)
    
    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_asset_path(asset_path: Path) -> bool:
    """
    Valida que un path de asset sea seguro.
    
    Args:
        asset_path: Path a validar
        
    Returns:
        True si es válido
    """
    # Verificar que no sea path traversal
    try:
        asset_path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return False
    
    # Verificar que exista
    if not asset_path.exists():
        return False
    
    # Verificar que sea un archivo (no directorio)
    if not asset_path.is_file():
        return False
    
    return True


def validate_video_file(video_path: Path) -> Tuple[bool, str]:
    """
    Valida que un archivo sea un video válido.
    
    Args:
        video_path: Path al video
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not video_path.exists():
        return False, f"Video no existe: {video_path}"
    
    # Verificar extensión
    valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    if video_path.suffix.lower() not in valid_extensions:
        return False, f"Extensión inválida: {video_path.suffix}"
    
    # Verificar tamaño (máximo 500MB)
    max_size = 500 * 1024 * 1024  # 500MB
    if video_path.stat().st_size > max_size:
        return False, f"Video demasiado grande: {video_path.stat().st_size / (1024*1024):.2f}MB"
    
    # TODO: Verificar con ffprobe que sea un video válido
    # Por ahora, solo verificamos que exista y tenga extensión válida
    
    return True, ""


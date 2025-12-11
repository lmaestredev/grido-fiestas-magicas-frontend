"""
Script para subir imagen de Papá Noel a D-ID.

Este script sube la imagen de Papá Noel a D-ID y muestra la URL resultante
que se puede usar como source_url en los talks.

Uso:
    python scripts/upload_image_to_did.py
    python scripts/upload_image_to_did.py --image-path assets/Grido_PapaNoel.png
"""

import os
import sys
import base64
import requests
import argparse
from pathlib import Path

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
if str(worker_dir) not in sys.path:
    sys.path.insert(0, str(worker_dir))

# Cargar variables de entorno
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_did_auth_headers():
    """Obtiene los headers de autenticación para D-ID API."""
    # D-ID usa Basic Authentication con Base64
    api_key_encoded = os.getenv("DID_API_KEY")
    api_key_plain = os.getenv("DID_API_KEY_PLAIN")
    
    if api_key_encoded:
        # Si está en env como DID_API_KEY, asumir que ya está codificado
        api_key = api_key_encoded
    elif api_key_plain:
        # Si está como DID_API_KEY_PLAIN, codificar a Base64
        # D-ID usa formato: base64(api_key:)
        api_key_with_colon = f"{api_key_plain}:"
        api_key = base64.b64encode(api_key_with_colon.encode()).decode()
    else:
        raise Exception(
            "D-ID API key no configurada. "
            "Configura DID_API_KEY o DID_API_KEY_PLAIN en .env"
        )
    
    return {
        "accept": "application/json",
        "authorization": f"Basic {api_key}",
    }


def upload_image_to_did(image_path: Path) -> str:
    """
    Sube una imagen a D-ID y retorna la source_url.
    
    Args:
        image_path: Path a la imagen a subir
        
    Returns:
        source_url de la imagen subida
    """
    if not image_path.exists():
        raise Exception(f"Imagen no encontrada: {image_path}")
    
    api_base_url = os.getenv("DID_API_BASE_URL", "https://api.d-id.com")
    url = f"{api_base_url}/images"
    headers = get_did_auth_headers()
    
    print(f"📤 Subiendo imagen a D-ID: {image_path}")
    print(f"   Tamaño: {image_path.stat().st_size / 1024:.2f} KB")
    
    try:
        with open(image_path, "rb") as f:
            files = {"image": (image_path.name, f, "image/png")}
            response = requests.post(url, files=files, headers=headers, timeout=30)
        
        if response.status_code not in (200, 201):
            try:
                error_data = response.json()
            except Exception:
                error_data = response.text[:500]
            raise Exception(f"D-ID upload image failed: {error_data}")
        
        result = response.json()
        # D-ID retorna {"url": "...", "id": "..."}
        source_url = result.get("url") or result.get("source_url")
        image_id = result.get("id")
        
        if not source_url:
            raise Exception(f"D-ID no retornó URL de imagen: {result}")
        
        print(f"✅ Imagen subida exitosamente!")
        print(f"   Image ID: {image_id}")
        print(f"   Source URL: {source_url}")
        print()
        print("💡 Puedes usar esta URL como source_url en los talks de D-ID")
        print(f"   O configurarla en .env como: DID_PAPA_NOEL_IMAGE_URL={source_url}")
        
        return source_url
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error subiendo imagen a D-ID: {str(e)}")


def find_papa_noel_image() -> Path:
    """
    Busca la imagen de Papá Noel en varios lugares posibles.
    
    Returns:
        Path a la imagen encontrada
        
    Raises:
        Exception: Si no se encuentra la imagen
    """
    possible_paths = [
        Path(os.getenv("PAPA_NOEL_IMAGE_PATH", "")),
        worker_dir / "assets" / "Grido_PapaNoel.png",
        worker_dir.parent / "assets" / "Grido_PapaNoel.png",
        Path("assets/Grido_PapaNoel.png"),
        Path("../assets/Grido_PapaNoel.png"),
        Path("grido-backend/assets/Grido_PapaNoel.png"),
        Path("grido-backend/worker/assets/Grido_PapaNoel.png"),
    ]
    
    for path in possible_paths:
        if path and path.exists():
            return path
    
    raise Exception(
        f"Imagen de Papá Noel no encontrada. Buscado en: {possible_paths}. "
        "Especifica la ruta con --image-path"
    )


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Sube imagen de Papá Noel a D-ID"
    )
    parser.add_argument(
        "--image-path",
        type=str,
        help="Ruta a la imagen a subir (default: busca automáticamente)"
    )
    parser.add_argument(
        "--save-url",
        action="store_true",
        help="Guardar la URL en un archivo .env.local"
    )
    
    args = parser.parse_args()
    
    try:
        # Obtener ruta de imagen
        if args.image_path:
            image_path = Path(args.image_path)
        else:
            print("🔍 Buscando imagen de Papá Noel...")
            image_path = find_papa_noel_image()
            print(f"   Encontrada en: {image_path}")
        
        # Subir imagen
        source_url = upload_image_to_did(image_path)
        
        # Opcional: guardar URL en .env.local
        if args.save_url:
            env_file = Path(".env.local")
            if not env_file.exists():
                env_file = Path(".env")
            
            # Leer archivo .env existente
            env_content = ""
            if env_file.exists():
                env_content = env_file.read_text()
            
            # Agregar o actualizar DID_PAPA_NOEL_IMAGE_URL
            if "DID_PAPA_NOEL_IMAGE_URL" in env_content:
                # Actualizar línea existente
                lines = env_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("DID_PAPA_NOEL_IMAGE_URL"):
                        lines[i] = f"DID_PAPA_NOEL_IMAGE_URL={source_url}"
                        break
                env_content = "\n".join(lines)
            else:
                # Agregar nueva línea
                if env_content and not env_content.endswith("\n"):
                    env_content += "\n"
                env_content += f"DID_PAPA_NOEL_IMAGE_URL={source_url}\n"
            
            env_file.write_text(env_content)
            print(f"💾 URL guardada en {env_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


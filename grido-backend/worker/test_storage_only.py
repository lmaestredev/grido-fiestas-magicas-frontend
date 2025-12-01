"""
Script de prueba SOLO para storage (sin generar video).

Este script prueba únicamente la funcionalidad de storage:
- Crea un video de prueba (simulado)
- Lo sube al storage configurado
- Verifica que la URL funcione

Uso:
    python test_storage_only.py
"""

import os
import sys
from pathlib import Path
import tempfile
import shutil

# Agregar el directorio del worker al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_storage_only():
    """Prueba solo la funcionalidad de storage."""
    print()
    print("🧪 Prueba de Storage - Grido Video Worker")
    print("=" * 60)
    print()
    
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    print(f"📦 Tipo de storage: {storage_type}")
    print()
    
    # Crear un archivo de prueba (simulando un video)
    print("📝 Creando archivo de prueba...")
    temp_dir = Path(tempfile.mkdtemp())
    test_video = temp_dir / "test_video.mp4"
    
    # Crear un archivo dummy (1MB de datos)
    with open(test_video, "wb") as f:
        f.write(b"0" * (1024 * 1024))  # 1MB de ceros
    
    print(f"   ✅ Archivo creado: {test_video}")
    print(f"   📊 Tamaño: {test_video.stat().st_size / (1024 * 1024):.2f} MB")
    print()
    
    # Intentar subir
    try:
        print(f"📤 Subiendo a {storage_type}...")
        from storage import upload_video
        
        video_id = f"test_storage_{int(__import__('time').time())}"
        video_url = upload_video(video_id, test_video)
        
        print()
        print("✅ ¡Upload exitoso!")
        print(f"   🆔 Video ID: {video_id}")
        print(f"   🔗 URL: {video_url}")
        print()
        
        # Verificar que la URL sea accesible (solo para URLs HTTP/HTTPS)
        if video_url.startswith("http"):
            print("🔍 Verificando accesibilidad de la URL...")
            import requests
            try:
                response = requests.head(video_url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    print(f"   ✅ URL accesible (Status: {response.status_code})")
                else:
                    print(f"   ⚠️  URL responde con status: {response.status_code}")
            except Exception as e:
                print(f"   ⚠️  No se pudo verificar URL: {e}")
        elif video_url.startswith("file://"):
            print("   ℹ️  URL local (file://) - no se puede verificar remotamente")
            local_path = video_url.replace("file://", "")
            if Path(local_path).exists():
                print(f"   ✅ Archivo existe localmente: {local_path}")
            else:
                print(f"   ❌ Archivo no encontrado: {local_path}")
        
        print()
        print("=" * 60)
        print("✅ Prueba de storage completada exitosamente!")
        return True
        
    except Exception as e:
        print()
        print(f"❌ Error durante el upload: {str(e)}")
        import traceback
        traceback.print_exc()
        print()
        print("=" * 60)
        print("❌ La prueba de storage falló.")
        return False
    finally:
        # Limpiar archivo temporal
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == "__main__":
    success = test_storage_only()
    sys.exit(0 if success else 1)


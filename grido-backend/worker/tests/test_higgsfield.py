import os
import sys
from pathlib import Path
import tempfile

# Asegurar path al worker
worker_dir = Path(__file__).parent.parent
sys.path.insert(0, str(worker_dir))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def test_higgsfield_provider():
    """Test directo del provider de Higgsfield."""

    print("\n🎬 Test de Higgsfield Video Provider")
    print("=" * 60)

    api_key = os.getenv("HIGGSFIELD_API_KEY")
    api_key_id = os.getenv("HIGGSFIELD_API_KEY_ID")
    api_key_secret = os.getenv("HIGGSFIELD_API_KEY_SECRET")

    if not (api_key or (api_key_id and api_key_secret)):
        print("❌ Higgsfield no configurado.")
        print("   Configura en .env al menos uno de:")
        print("   - HIGGSFIELD_API_KEY=...")
        print("   - HIGGSFIELD_API_KEY_ID=... y HIGGSFIELD_API_KEY_SECRET=...")
        return False

    print("✅ Credenciales de Higgsfield detectadas")
    print(f"   HIGGSFIELD_API_KEY: {'set' if api_key else 'no'}")
    print(f"   HIGGSFIELD_API_KEY_ID: {'set' if api_key_id else 'no'}")
    print(f"   HIGGSFIELD_API_KEY_SECRET: {'set' if api_key_secret else 'no'}")
    print()

    from providers.higgsfield_video import HiggsfieldVideoProvider

    provider = HiggsfieldVideoProvider()
    if not provider.is_available():
        print("❌ Higgsfield provider no está disponible (is_available()=False)")
        return False

    print("✅ Higgsfield provider inicializado correctamente\n")

    # Prompt sencillo de prueba
    script = "Santa Claus is greeting you. Merry Christmas from Higgsfield!"

    temp_dir = Path(tempfile.mkdtemp())
    output_path = temp_dir / "higgsfield_test_video.mp4"

    try:
        print("🎥 Generando video con Higgsfield...")
        print("   (Esto puede tardar varios minutos)\n")

        result = provider.generate_video(
            script=script,
            avatar_id="",        # Higgsfield puede ignorar esto
            output_path=output_path,
            duration=10,         # segundos, si la API lo soporta
        )

        if not result.exists():
            print("❌ El video no se generó en el path esperado")
            return False

        size_mb = result.stat().st_size / (1024 * 1024)
        print("\n✅ Video generado exitosamente con Higgsfield")
        print(f"   📁 Ubicación: {result}")
        print(f"   📊 Tamaño: {size_mb:.2f} MB\n")
        return True

    except Exception as e:
        print(f"\n❌ Error durante la generación con Higgsfield: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ok = test_higgsfield_provider()
    sys.exit(0 if ok else 1)
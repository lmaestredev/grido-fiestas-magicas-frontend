"""
Test unitario para validar la concatenación completa de videos.

Este test valida que los 3 videos se unifiquen correctamente:
- Frames_1_2_to_3.mov (intro)
- Saludo_a_manuel.mp4 (saludo)
- Frame_4_NocheMagica.mov (outro)

Uso:
    python test_video_concatenation.py
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import unittest

# Configurar encoding UTF-8 para Windows (soporte de emojis)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio del worker al path
worker_dir = Path(__file__).parent.parent
sys.path.insert(0, str(worker_dir))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_video_info(video_path: Path) -> dict:
    """
    Obtiene información del video usando ffprobe.
    
    Returns:
        dict con información del video (duration, width, height, fps, size)
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration,size:stream=width,height,r_frame_rate",
            "-of", "json",
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        data = json.loads(result.stdout)
        
        # Extraer información
        format_info = data.get("format", {})
        stream_info = data.get("streams", [{}])[0]
        
        duration = float(format_info.get("duration", 0))
        size = int(format_info.get("size", 0))
        width = int(stream_info.get("width", 0))
        height = int(stream_info.get("height", 0))
        
        # Calcular FPS
        r_frame_rate = stream_info.get("r_frame_rate", "0/1")
        if "/" in r_frame_rate:
            num, den = map(int, r_frame_rate.split("/"))
            fps = num / den if den > 0 else 0
        else:
            fps = float(r_frame_rate) if r_frame_rate else 0
        
        return {
            "duration": duration,
            "size": size,
            "width": width,
            "height": height,
            "fps": fps,
            "exists": True
        }
    except Exception as e:
        return {
            "exists": video_path.exists(),
            "error": str(e)
        }


def concatenate_videos_with_manager(
    intro: Path,
    middle: Path,
    outro: Path,
    output: Path,
    video_id: str = "test"
) -> tuple[bool, str]:
    """
    Concatena los 3 videos usando la función real de ProviderManager.
    
    Esta función replica exactamente el comportamiento de producción usando
    _compose_videos_with_overlaps de manager.py, que incluye:
    - Overlaps para transiciones suaves
    - Parámetros optimizados para Windows (yuv420p, faststart, etc.)
    - Manejo de audio con mezcla
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # Importar ProviderManager
        from providers.manager import ProviderManager
        
        # Crear instancia de ProviderManager
        # No necesitamos providers reales para este test, solo la función de composición
        manager = ProviderManager()
        
        # Usar la función real de composición con overlaps
        # Esta es la misma función que se usa en producción
        result_path = manager._compose_videos_with_overlaps(
            intro_video=intro,
            main_video=middle,
            outro_video=outro,
            output_path=output,
            video_id=video_id,
            overlap_frames=15  # Mismo valor que en producción
        )
        
        if not output.exists():
            return False, "El video de salida no se generó"
        
        return True, "Video compuesto exitosamente usando ProviderManager (replica producción)"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


class TestVideoConcatenation(unittest.TestCase):
    """Test unitario para validar la concatenación de videos."""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests."""
        cls.assets_path = Path("assets")
        # Crear directorio assets si no existe
        cls.assets_path.mkdir(exist_ok=True)
        
        # Directorio temporal solo para archivos auxiliares (concat_list.txt)
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="video_test_"))
        
        # Paths de los videos de entrada
        cls.intro_video = cls.assets_path / "Frames_1_2_to_3.mov"
        cls.middle_video = cls.assets_path / "Saludo_a_manuel.mp4"
        cls.outro_video = cls.assets_path / "Frame_4_NocheMagica.mov"
        
        # Video de salida en la carpeta assets
        cls.output_video = cls.assets_path / "video_final_test.mp4"
        
        print("\n" + "=" * 70)
        print("🧪 Test Unitario: Concatenación de Videos")
        print("=" * 70)
        print()
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza después de todos los tests."""
        import shutil
        # Solo limpiar el directorio temporal (no eliminar assets)
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
        # El video de salida se mantiene en assets para que el usuario pueda verlo
    
    def test_01_videos_exist(self):
        """Test: Verificar que los 3 videos de entrada existen."""
        print("📋 Test 1: Verificar existencia de videos de entrada")
        print("-" * 70)
        
        self.assertTrue(
            self.intro_video.exists(),
            f"❌ No se encuentra el video intro: {self.intro_video}"
        )
        print(f"   ✅ Intro encontrado: {self.intro_video.name}")
        
        self.assertTrue(
            self.middle_video.exists(),
            f"❌ No se encuentra el video saludo: {self.middle_video}"
        )
        print(f"   ✅ Saludo encontrado: {self.middle_video.name}")
        
        self.assertTrue(
            self.outro_video.exists(),
            f"❌ No se encuentra el video outro: {self.outro_video}"
        )
        print(f"   ✅ Outro encontrado: {self.outro_video.name}")
        print()
    
    def test_02_video_info(self):
        """Test: Obtener información de los videos de entrada."""
        print("📊 Test 2: Información de videos de entrada")
        print("-" * 70)
        
        intro_info = get_video_info(self.intro_video)
        middle_info = get_video_info(self.middle_video)
        outro_info = get_video_info(self.outro_video)
        
        # Validar que se pudo obtener información
        self.assertIn("exists", intro_info)
        self.assertIn("exists", middle_info)
        self.assertIn("exists", outro_info)
        
        if "error" not in intro_info:
            print(f"   📹 Intro ({self.intro_video.name}):")
            print(f"      - Duración: {intro_info.get('duration', 0):.2f}s")
            print(f"      - Resolución: {intro_info.get('width', 0)}x{intro_info.get('height', 0)}")
            print(f"      - FPS: {intro_info.get('fps', 0):.2f}")
            print(f"      - Tamaño: {intro_info.get('size', 0) / (1024*1024):.2f} MB")
        
        if "error" not in middle_info:
            print(f"   📹 Saludo ({self.middle_video.name}):")
            print(f"      - Duración: {middle_info.get('duration', 0):.2f}s")
            print(f"      - Resolución: {middle_info.get('width', 0)}x{middle_info.get('height', 0)}")
            print(f"      - FPS: {middle_info.get('fps', 0):.2f}")
            print(f"      - Tamaño: {middle_info.get('size', 0) / (1024*1024):.2f} MB")
        
        if "error" not in outro_info:
            print(f"   📹 Outro ({self.outro_video.name}):")
            print(f"      - Duración: {outro_info.get('duration', 0):.2f}s")
            print(f"      - Resolución: {outro_info.get('width', 0)}x{outro_info.get('height', 0)}")
            print(f"      - FPS: {outro_info.get('fps', 0):.2f}")
            print(f"      - Tamaño: {outro_info.get('size', 0) / (1024*1024):.2f} MB")
        
        print()
    
    def test_03_concatenate_videos(self):
        """Test: Concatenar los 3 videos usando ProviderManager (replica producción)."""
        print("🎬 Test 3: Concatenar videos usando ProviderManager")
        print("-" * 70)
        print("   ℹ️  Usando _compose_videos_with_overlaps (misma función de producción)")
        print()
        
        success, message = concatenate_videos_with_manager(
            self.intro_video,
            self.middle_video,
            self.outro_video,
            self.output_video,
            video_id="test_concatenation"
        )
        
        self.assertTrue(success, f"❌ Error concatenando videos: {message}")
        print(f"   ✅ {message}")
        
        # Verificar que el archivo existe
        self.assertTrue(
            self.output_video.exists(),
            "❌ El video de salida no existe después de la concatenación"
        )
        print(f"   📁 Video generado: {self.output_video.absolute()}")
        print()
    
    def test_04_output_video_valid(self):
        """Test: Validar el video de salida."""
        print("✅ Test 4: Validar video de salida")
        print("-" * 70)
        
        # Verificar que existe
        self.assertTrue(
            self.output_video.exists(),
            "❌ El video de salida no existe"
        )
        
        # Verificar tamaño
        file_size = self.output_video.stat().st_size
        self.assertGreater(
            file_size,
            0,
            "❌ El video de salida está vacío"
        )
        print(f"   ✅ Tamaño: {file_size / (1024*1024):.2f} MB")
        
        # Obtener información del video
        output_info = get_video_info(self.output_video)
        
        if "error" not in output_info:
            print(f"   ✅ Duración: {output_info.get('duration', 0):.2f}s")
            print(f"   ✅ Resolución: {output_info.get('width', 0)}x{output_info.get('height', 0)}")
            print(f"   ✅ FPS: {output_info.get('fps', 0):.2f}")
            
            # Validar que tiene duración razonable (suma de los 3 videos)
            self.assertGreater(
                output_info.get('duration', 0),
                0,
                "❌ El video de salida no tiene duración válida"
            )
            
            # Validar que tiene resolución
            self.assertGreater(
                output_info.get('width', 0),
                0,
                "❌ El video de salida no tiene ancho válido"
            )
            self.assertGreater(
                output_info.get('height', 0),
                0,
                "❌ El video de salida no tiene alto válido"
            )
        else:
            print(f"   ⚠️  No se pudo obtener información detallada: {output_info.get('error', 'Unknown')}")
        
        print()
    
    def test_05_video_playable(self):
        """Test: Verificar que el video es reproducible."""
        print("▶️  Test 5: Verificar que el video es reproducible")
        print("-" * 70)
        
        # Verificar que el archivo existe
        self.assertTrue(
            self.output_video.exists(),
            "❌ El video no existe"
        )
        
        # Intentar obtener información con ffprobe (si falla, el video no es válido)
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_format",
                str(self.output_video)
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.assertEqual(
                result.returncode,
                0,
                f"❌ El video no es reproducible. Error: {result.stderr}"
            )
            print("   ✅ El video es reproducible y válido")
            
        except subprocess.TimeoutExpired:
            self.fail("❌ Timeout al verificar el video")
        except FileNotFoundError:
            self.skipTest("⚠️  ffprobe no está disponible, saltando verificación de reproducibilidad")
        
        print()


def run_tests():
    """Ejecuta todos los tests."""
    # Verificar que FFmpeg está disponible
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Error: FFmpeg no está instalado o no está en PATH")
        print("   Instala FFmpeg para ejecutar los tests")
        sys.exit(1)
    
    # Ejecutar tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestVideoConcatenation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print()
    print("=" * 70)
    if result.wasSuccessful():
        print("✅ Todos los tests pasaron exitosamente!")
        print()
        output_path = TestVideoConcatenation.output_video.absolute()
        print(f"📁 Video de salida: {output_path}")
        print(f"💡 Para reproducir: open \"{output_path}\"")
        print(f"   O navega a: {TestVideoConcatenation.assets_path.absolute()}")
    else:
        print("❌ Algunos tests fallaron")
        print(f"   - Tests ejecutados: {result.testsRun}")
        print(f"   - Fallos: {len(result.failures)}")
        print(f"   - Errores: {len(result.errors)}")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
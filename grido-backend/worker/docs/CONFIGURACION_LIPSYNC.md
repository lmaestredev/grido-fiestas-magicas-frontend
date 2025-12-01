# Configuración de Lip-Sync Providers

Este documento explica cómo configurar MuseTalk y Wav2Lip para lip-sync local.

## MuseTalk

### Opción 1: Instalación como Paquete Python

```bash
pip install musetalk
```

### Opción 2: Instalación desde Repositorio

```bash
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk
pip install -r requirements.txt
```

### Variables de Entorno

Agregar al `.env`:

```bash
# MuseTalk
MUSETALK_MODEL_PATH=/path/to/musetalk/model
MUSETALK_SCRIPT_PATH=musetalk/realtime_inference.py
```

### Verificación

```bash
python -c "import musetalk; print('MuseTalk instalado correctamente')"
```

## Wav2Lip

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos (requerido)
# wav2lip_gan.pth - Modelo principal
# s3fd.pth - Face detection model (opcional pero recomendado)
```

### Descargar Modelos

Los modelos se pueden descargar desde:
- https://github.com/Rudrabha/Wav2Lip#pre-trained-models

### Variables de Entorno

Agregar al `.env`:

```bash
# Wav2Lip
WAV2LIP_REPO_PATH=/path/to/Wav2Lip
WAV2LIP_MODEL_PATH=/path/to/Wav2Lip/checkpoints/wav2lip_gan.pth
WAV2LIP_FACE_DET_MODEL=/path/to/Wav2Lip/face_detection/s3fd.pth  # Opcional
```

### Verificación

```bash
cd Wav2Lip
python inference.py --checkpoint_path checkpoints/wav2lip_gan.pth --face test_video.mp4 --audio test_audio.wav --outfile output.mp4
```

## Orden de Preferencia

El sistema intentará usar los providers en este orden:

1. **MuseTalk** (preferido - más rápido y preciso)
2. **Wav2Lip** (fallback - open-source, más lento pero funcional)

## Deshabilitar Providers

Si no quieres usar un provider específico:

```bash
# Deshabilitar MuseTalk
DISABLE_MUSETALK=true

# Deshabilitar Wav2Lip
DISABLE_WAV2LIP=true
```

## Requisitos del Sistema

### MuseTalk
- Python 3.8+
- GPU recomendada (CUDA) para mejor rendimiento
- ~2GB RAM mínimo

### Wav2Lip
- Python 3.6+
- GPU recomendada (CUDA) para mejor rendimiento
- ~4GB RAM mínimo
- FFmpeg instalado

## Troubleshooting

### MuseTalk no se detecta

1. Verificar que esté instalado: `pip list | grep musetalk`
2. Verificar variables de entorno en `.env`
3. Verificar que el modelo existe si se especificó `MUSETALK_MODEL_PATH`

### Wav2Lip no se detecta

1. Verificar que el repositorio esté clonado
2. Verificar que `inference.py` exista en `WAV2LIP_REPO_PATH`
3. Verificar que el modelo `wav2lip_gan.pth` exista
4. Verificar variables de entorno en `.env`

### Error: "CUDA out of memory"

- Reducir el tamaño del video de entrada
- Usar CPU en lugar de GPU (más lento)
- Cerrar otras aplicaciones que usen GPU


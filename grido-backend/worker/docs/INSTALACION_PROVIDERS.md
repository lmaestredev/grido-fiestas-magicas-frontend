# Instalación de Providers - Guía Completa

## Resumen de Providers Disponibles

### TTS (Text-to-Speech)
- ✅ **ElevenLabs**: API-based, funciona (requiere API key)
- ⚠️ **Kokoro**: Local, requiere configuración

### Lip-Sync
- ⚠️ **MuseTalk**: Local, requiere instalación
- ⚠️ **Wav2Lip**: Local, requiere instalación

### Video Completo
- ⚠️ **HeyGen**: API-based, requiere corrección de endpoint

## Instalación Rápida

### 1. ElevenLabs (Ya Funciona) ✅

Solo requiere API key en `.env`:
```bash
ELEVENLABS_API_KEY=tu_api_key_aqui
PAPA_NOEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Opcional
```

### 2. MuseTalk (Recomendado para Lip-Sync)

```bash
# Opción A: Instalar como paquete
pip install musetalk

# Opción B: Instalar desde repositorio
git clone https://github.com/TMElyralab/MuseTalk.git
cd MuseTalk
pip install -r requirements.txt
```

Agregar a `.env`:
```bash
MUSETALK_MODEL_PATH=/path/to/model  # Opcional
MUSETALK_SCRIPT_PATH=musetalk/realtime_inference.py  # Opcional
```

### 3. Wav2Lip (Alternativa Open-Source)

```bash
# Clonar repositorio
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelos (requerido)
# Descargar wav2lip_gan.pth desde:
# https://github.com/Rudrabha/Wav2Lip#pre-trained-models
```

Agregar a `.env`:
```bash
WAV2LIP_REPO_PATH=/path/to/Wav2Lip
WAV2LIP_MODEL_PATH=/path/to/Wav2Lip/checkpoints/wav2lip_gan.pth
```

### 4. HeyGen (Requiere Corrección)

Solo requiere API key (pero endpoint necesita corrección):
```bash
HEYGEN_API_KEY=tu_api_key_aqui
PAPA_NOEL_AVATAR_ID=tu_avatar_id  # Opcional
```

## Orden de Fallback

El sistema intentará usar los providers en este orden:

### Para TTS:
1. ElevenLabs (si está configurado)
2. Kokoro (si está instalado)

### Para Lip-Sync:
1. MuseTalk (si está instalado)
2. Wav2Lip (si está instalado)

### Para Video Completo:
1. Strategy 1: TTS + Lip-Sync (MuseTalk o Wav2Lip)
2. Strategy 2: HeyGen (si funciona)
3. Strategy 3: TTS + Base Video (sin lip-sync) ✅ **Ya funciona**

## Verificación

### Verificar Providers Disponibles

```bash
cd grido-backend/worker
source venv/bin/activate
python3 -c "from providers.manager import ProviderManager; m = ProviderManager(); print(f'TTS: {len(m.tts_providers)}, Lip-sync: {len(m.lipsync_providers)}, Video: {len(m.video_providers)}')"
```

### Probar TTS

```bash
python3 test_audio_generation.py
```

### Probar Lip-Sync (si está instalado)

```bash
# Requiere video base y audio
python3 -c "
from providers.manager import ProviderManager
from pathlib import Path
m = ProviderManager()
if m.lipsync_providers:
    print(f'Lip-sync disponible: {m.lipsync_providers[0].__class__.__name__}')
else:
    print('No hay lip-sync providers disponibles')
"
```

## Estado Actual

- ✅ **ElevenLabs TTS**: Funcionando
- ✅ **Strategy 3 (TTS + Base Video)**: Funcionando (sin lip-sync)
- ⚠️ **MuseTalk**: Requiere instalación
- ⚠️ **Wav2Lip**: Requiere instalación
- ⚠️ **HeyGen**: Requiere corrección de endpoint

## Próximos Pasos

1. **Corto plazo**: Usar Strategy 3 (ya funciona)
2. **Mediano plazo**: Instalar MuseTalk o Wav2Lip para lip-sync
3. **Largo plazo**: Corregir HeyGen cuando se tenga acceso a documentación completa


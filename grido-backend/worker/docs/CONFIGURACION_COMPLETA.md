# Configuración Completa del Sistema

## ✅ Cambios Implementados

### 1. Sistema de Configuración de Papá Noel ✅

**Archivo**: `papa_noel_config.py`

**Características:**
- ✅ Voice ID configurable (ElevenLabs)
- ✅ Avatar ID configurable (HeyGen)
- ✅ Personalidad y contexto de Papá Noel
- ✅ Plantillas de diálogos
- ✅ Frases típicas organizadas por categoría
- ✅ Funciones para generar scripts personalizados

**Uso:**
```python
from papa_noel_config import (
    generate_frame2_script,
    generate_frame3_script,
    get_papa_noel_voice_id,
    get_papa_noel_avatar_id,
)

# Generar scripts
script_frame2 = generate_frame2_script()
script_frame3 = generate_frame3_script(form_data)

# Obtener IDs
voice_id = get_papa_noel_voice_id()
avatar_id = get_papa_noel_avatar_id()
```

**Variables de entorno:**
```bash
PAPA_NOEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Voice ID de ElevenLabs
PAPA_NOEL_AVATAR_ID=default              # Avatar ID de HeyGen
```

---

### 2. Higgsfield Video Provider ✅

**Archivo**: `providers/higgsfield_video.py`

**Estado**: Implementado y agregado al ProviderManager

**Configuración:**
```bash
HIGGSFIELD_API_KEY=tu_api_key_aqui
HIGGSFIELD_API_BASE_URL=https://cloud.higgsfield.ai/api  # Opcional
```

**Nota**: Según investigación, Higgsfield puede no tener API pública oficial. 
Si no funciona, se puede deshabilitar con:
```bash
DISABLE_HIGGSFIELD=true
```

---

### 3. Strategy 1 - Configuración Mejorada ✅

**Providers de Lip-Sync disponibles:**
1. **MuseTalk** (local, open-source)
2. **Sync Labs** (API comercial HD) ⭐
3. **Wav2Lip** (local, open-source)

**Configuración requerida:**

#### MuseTalk:
```bash
MUSETALK_REPO_PATH=/path/to/MuseTalk
MUSETALK_SCRIPT_PATH=scripts/realtime_inference.py  # Opcional
MUSETALK_MODEL_PATH=/path/to/model  # Opcional
```

#### Sync Labs (Recomendado):
```bash
SYNCLABS_API_KEY=tu_api_key
```

#### Wav2Lip:
```bash
WAV2LIP_REPO_PATH=/path/to/wav2lip
WAV2LIP_MODEL_PATH=/path/to/wav2lip/checkpoints/wav2lip_gan.pth
```

**Orden de fallback:**
```
1. MuseTalk
   ↓ (si falla)
2. Sync Labs ⭐
   ↓ (si falla)
3. Wav2Lip
```

---

### 4. HeyGen - Diagnóstico ✅

**Script de diagnóstico**: `test_heygen_fix.py`

**Problema identificado:**
- Todos los endpoints retornan 404
- Posibles causas:
  - API key inválida/expirada
  - Endpoints cambiados (API v3?)
  - Requiere autenticación diferente

**Acciones recomendadas:**
1. Verificar API key en dashboard: https://app.heygen.com/login
2. Revisar documentación: https://docs.heygen.com
3. Contactar soporte si es necesario

**Para probar:**
```bash
python test_heygen_fix.py
```

---

## 📋 Variables de Entorno Completas

```bash
# TTS
ELEVENLABS_API_KEY=tu_key
PAPA_NOEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Video Providers
HEYGEN_API_KEY=tu_key
PAPA_NOEL_AVATAR_ID=default
HIGGSFIELD_API_KEY=tu_key

# Lip-Sync
SYNCLABS_API_KEY=tu_key
MUSETALK_REPO_PATH=/path/to/MuseTalk
WAV2LIP_REPO_PATH=/path/to/wav2lip
WAV2LIP_MODEL_PATH=/path/to/model.pth

# Storage
STORAGE_TYPE=local  # local, firebase, vercel, s3, r2

# Redis
REDIS_URL=redis://localhost:6379

# Email
RESEND_API_KEY=tu_key
```

---

## 🚀 Flujo Completo Actualizado

```
1. Captura de datos del formulario
   ↓
2. Generación de scripts usando papa_noel_config
   ├─ Frame 2: generate_frame2_script()
   └─ Frame 3: generate_frame3_script(form_data)
   ↓
3. Strategy 1: TTS + Lip-sync
   ├─ TTS: ElevenLabs (con voice_id de Papá Noel)
   └─ Lip-sync:
       ├─ MuseTalk
       ├─ Sync Labs ⭐
       └─ Wav2Lip
   ↓ (si falla)
4. Strategy 2: Video Providers Completos
   ├─ Higgsfield (nuevo)
   └─ HeyGen (requiere fix)
   ↓ (si falla)
5. Strategy 3: TTS + Base Video
   └─ Funciona siempre (sin lip-sync)
```

---

## ✅ Próximos Pasos

1. **Configurar Sync Labs** (más fácil y confiable):
   ```bash
   SYNCLABS_API_KEY=tu_key
   ```

2. **Probar Strategy 1 con Sync Labs**:
   ```bash
   python test_flujo_completo_landing.py --direct
   ```

3. **Verificar HeyGen**:
   ```bash
   python test_heygen_fix.py
   ```

4. **Probar Higgsfield** (si tienes API key):
   ```bash
   HIGGSFIELD_API_KEY=tu_key python test_flujo_completo_landing.py --direct
   ```

---

## 📝 Notas

- **Strategy 3 funciona ahora mismo** sin configuración adicional
- **Sync Labs es la opción más confiable** para lip-sync (API comercial)
- **papa_noel_config.py** centraliza toda la configuración de voz y diálogos
- **Higgsfield** está implementado pero puede no tener API pública


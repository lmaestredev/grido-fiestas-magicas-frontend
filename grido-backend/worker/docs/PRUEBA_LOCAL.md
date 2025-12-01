# Guía de Prueba Local

Esta guía te permite probar el worker de generación de video localmente sin necesidad de Modal, Redis, o storage remoto.

## Requisitos Previos

1. **Python 3.9+** instalado
2. **FFmpeg** instalado y en PATH
3. **Videos base** en `assets/`:
   - `Frames_1_2_to_3.mov`
   - `Frame_4_NocheMagica.mov`
   - `frame3_santa_base.mp4` (opcional, solo para Strategy 1)

## Instalación

```bash
cd grido-backend/worker

# Instalar dependencias
pip install -r requirements.txt

# Instalar providers según necesites:
# Para ElevenLabs TTS:
# pip install elevenlabs

# Para HeyGen:
# pip install heygen-api  # o según su SDK

# Para Firebase Storage (opcional):
# pip install firebase-admin

# Para Vercel Blob (opcional):
# pip install vercel-blob
```

## Configuración

Crea un archivo `.env` en `grido-backend/worker/` con las variables necesarias:

```bash
# Storage (elige uno)
STORAGE_TYPE=local  # opciones: local, firebase, vercel, railway, s3, r2
LOCAL_STORAGE_PATH=./storage  # solo si STORAGE_TYPE=local

# Para Firebase Storage:
# STORAGE_TYPE=firebase
# FIREBASE_STORAGE_BUCKET=grido-56fa7.firebasestorage.app
# FIREBASE_CREDENTIALS_PATH=./grido-56fa7-firebase-adminsdk-xxxxx.json
# O usar FIREBASE_CREDENTIALS_JSON (JSON string en una línea)
# Ver FIREBASE_SETUP.md para más detalles

# Para Vercel Blob:
# STORAGE_TYPE=vercel
# VERCEL_BLOB_TOKEN=tu-token

# Para Railway:
# STORAGE_TYPE=railway
# RAILWAY_STORAGE_PATH=/app/storage
# API_BASE_URL=https://tu-api.railway.app

# Para S3/R2:
# STORAGE_TYPE=s3  # o r2
# AWS_ACCESS_KEY_ID=tu-key
# AWS_SECRET_ACCESS_KEY=tu-secret
# S3_BUCKET=tu-bucket
# AWS_REGION=us-east-1
# AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com  # solo para R2

# Providers (al menos uno debe estar configurado)
ELEVENLABS_API_KEY=tu-key  # Para TTS
HEYGEN_API_KEY=tu-key  # Para video completo
KOKORO_MODEL_PATH=./models/kokoro  # Si usas Kokoro TTS
MUSETALK_MODEL_PATH=./models/musetalk  # Si usas MuseTalk

# Deshabilitar providers si no los usas
# DISABLE_ELEVENLABS=true
# DISABLE_KOKORO=true
# DISABLE_MUSETALK=true
# DISABLE_HEYGEN=true
```

## Ejecutar Prueba Local

```bash
cd grido-backend/worker
python test_local.py
```

El script:
1. ✅ Verifica que los videos base existan
2. ✅ Verifica que haya al menos un provider disponible
3. ✅ Genera un video de prueba con datos de ejemplo
4. ✅ Guarda el video en `./storage/` (si `STORAGE_TYPE=local`)

## Opciones de Storage

### 1. Local (Recomendado para pruebas)

```bash
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage
```

El video se guarda localmente. Para servirlo:

```bash
# En otra terminal
cd storage
python -m http.server 8000
# Accede a http://localhost:8000/test_xxx.mp4
```

### 2. Firebase Storage

```bash
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

**Cómo obtener credenciales:**
1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Crea/selecciona proyecto
3. Storage → Crear bucket
4. Project Settings → Service Accounts → Generate new private key
5. Guarda el JSON como `firebase-credentials.json`

### 3. Vercel Blob

```bash
STORAGE_TYPE=vercel
VERCEL_BLOB_TOKEN=vercel_blob_xxx
```

**Cómo obtener token:**
1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Settings → Storage → Blob
3. Create → Copia el token

### 4. Railway

```bash
STORAGE_TYPE=railway
RAILWAY_STORAGE_PATH=/app/storage
API_BASE_URL=https://tu-api.railway.app
```

**Nota:** Railway no tiene storage dedicado. El video se guarda en un volumen persistente y debes crear un endpoint en tu API para servirlo.

### 5. S3 / Cloudflare R2

```bash
# Para S3:
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=tu-bucket
AWS_REGION=us-east-1

# Para R2:
STORAGE_TYPE=r2
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=tu-bucket
AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
```

## Solución de Problemas

### Error: "No se encuentra el directorio 'assets'"
- Asegúrate de ejecutar `test_local.py` desde `grido-backend/worker/`
- Verifica que los videos estén en `assets/`

### Error: "No hay providers disponibles"
- Configura al menos una API key:
  - `ELEVENLABS_API_KEY` para TTS
  - `HEYGEN_API_KEY` para video completo

### Error: "FFmpeg no encontrado"
- Instala FFmpeg:
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # Windows
  # Descarga desde https://ffmpeg.org/download.html
  ```

### Error: "firebase-admin no está instalado"
- Instala solo si usas Firebase:
  ```bash
  pip install firebase-admin
  ```

## Próximos Pasos

Una vez que la prueba local funcione:

1. ✅ Configura Redis (Upstash) para producción
2. ✅ Configura storage definitivo (Firebase/Vercel/R2)
3. ✅ Configura email (Resend)
4. ✅ Deploy del worker en Modal
5. ✅ Prueba end-to-end completa


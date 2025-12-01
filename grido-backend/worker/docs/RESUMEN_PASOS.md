# 📋 Resumen de Pasos - Flujo Completo

## ✅ Completado

1. ✅ **Storage configurado** - Firebase y Local funcionando
2. ✅ **Voz constante configurada** - Usa `PAPA_NOEL_VOICE_ID` siempre
3. ✅ **Scripts de prueba creados**:
   - `test_storage_only.py` - Prueba solo storage
   - `test_audio_generation.py` - Prueba generación de audio
   - `test_video_complete.py` - Prueba composición de video
   - `test_end_to_end.py` - Prueba flujo completo

---

## 🎯 Pasos para Probar el Flujo Completo

### Paso 1: Configurar Voz de Papá Noel

**ElevenLabs:**
1. Ve a [ElevenLabs Dashboard](https://elevenlabs.io/app)
2. Ve a **Voices** → Busca o crea una voz masculina cálida
3. Copia el Voice ID
4. Agrega a `.env`:
   ```bash
   PAPA_NOEL_VOICE_ID=tu_voice_id_aqui
   ```

**HeyGen:**
1. Ve a [HeyGen Dashboard](https://app.heygen.com)
2. Configura un avatar de Papá Noel
3. Copia el Avatar ID
4. Agrega a `.env`:
   ```bash
   PAPA_NOEL_AVATAR_ID=tu_avatar_id_aqui
   ```

---

### Paso 2: Probar Generación de Audio

```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_audio_generation.py
```

**Verificar:**
- ✅ Audio generado con voz correcta
- ✅ Formato WAV, 16kHz, mono
- ✅ Calidad adecuada

---

### Paso 3: Probar Composición de Video

```bash
python3 test_video_complete.py
```

**Verificar:**
- ✅ Video generado correctamente
- ✅ Audio sincronizado
- ✅ Intro + Frame3 + Outro compuestos
- ✅ Calidad y duración correctas

---

### Paso 4: Probar Upload a Firebase

**Primero, crear el bucket:**
- Seguir `CREAR_BUCKET_FIREBASE.md`

**Luego probar:**
```bash
# Configurar .env con Firebase
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Probar upload
python3 test_storage_only.py
```

**Verificar:**
- ✅ Video subido a Firebase
- ✅ URL pública generada
- ✅ URL accesible desde navegador

---

### Paso 5: Probar Flujo End-to-End

```bash
python3 test_end_to_end.py
```

**Verificar:**
- ✅ Audio generado con voz de Papá Noel
- ✅ Video compuesto correctamente
- ✅ Video subido a Firebase
- ✅ URL pública funcional

---

### Paso 6: Conectar Formulario → API

**6.1 Verificar API Route:**
- ✅ Ya existe: `grido_front/src/app/api/generate-video/route.ts`
- Verificar que Redis esté configurado

**6.2 Probar Formulario:**
```bash
cd grido_front
pnpm dev
```

**6.3 Llenar formulario y verificar:**
- Datos llegan a `/api/generate-video`
- Se encola en Redis
- Se retorna `videoId`

---

### Paso 7: Configurar Redis (Upstash)

1. Crear cuenta en [Upstash](https://console.upstash.com)
2. Crear base de datos Redis
3. Copiar credenciales:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
4. Agregar a `.env` del frontend:
   ```bash
   UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
   UPSTASH_REDIS_REST_TOKEN=xxx
   VIDEO_API_SECRET=tu_secret_aqui
   ```

---

### Paso 8: Configurar Email (Resend)

1. Crear cuenta en [Resend](https://resend.com)
2. Verificar dominio (o usar dominio de prueba)
3. Obtener API key
4. Agregar a `.env` del worker:
   ```bash
   RESEND_API_KEY=re_xxx
   ```

**Probar envío:**
- El worker envía email automáticamente después de subir video
- Verificar que email llega con URL del video

---

### Paso 9: Prueba Final End-to-End

**Flujo completo:**
1. Usuario llena formulario en landing
2. Formulario valida contenido (✅ ya implementado)
3. Se encola trabajo en Redis
4. Worker procesa:
   - Genera audio con voz de Papá Noel (✅ configurado)
   - Compone video (✅ implementado)
   - Sube a Firebase Storage (✅ implementado)
   - Obtiene URL pública (✅ implementado)
5. Worker envía email con URL (⏳ configurar Resend)
6. Usuario recibe email

---

## 📝 Variables de Entorno Necesarias

### Frontend (`.env.local`):
```bash
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
VIDEO_API_SECRET=tu_secret_aqui
PERSPECTIVE_API_KEY=xxx
```

### Backend Worker (`.env`):
```bash
# Voz de Papá Noel
PAPA_NOEL_VOICE_ID=tu_voice_id
PAPA_NOEL_AVATAR_ID=tu_avatar_id

# Providers
ELEVENLABS_API_KEY=xxx
HEYGEN_API_KEY=xxx

# Storage
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Email
RESEND_API_KEY=re_xxx

# Redis (para worker)
REDIS_URL=redis://xxx.upstash.io:6379
# O
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
```

---

## 🚀 Orden de Ejecución Recomendado

1. ✅ **Paso 1**: Configurar voz de Papá Noel
2. ✅ **Paso 2**: Probar generación de audio
3. ✅ **Paso 3**: Probar composición de video
4. ✅ **Paso 4**: Probar upload a Firebase
5. ✅ **Paso 5**: Probar flujo end-to-end local
6. ⏳ **Paso 6**: Conectar formulario → API
7. ⏳ **Paso 7**: Configurar Redis
8. ⏳ **Paso 8**: Configurar Email
9. ⏳ **Paso 9**: Prueba final end-to-end

---

## 📚 Archivos de Referencia

- `PLAN_PASOS_COMPLETO.md` - Plan detallado
- `CREAR_BUCKET_FIREBASE.md` - Crear bucket de Firebase
- `FIREBASE_SETUP.md` - Configuración de Firebase
- `PRUEBA_LOCAL.md` - Guía de pruebas locales


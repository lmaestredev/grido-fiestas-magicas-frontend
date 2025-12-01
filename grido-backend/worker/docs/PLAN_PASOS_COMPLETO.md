# Plan de Pasos - Flujo Completo de Generación de Video

## Objetivo
Probar el flujo completo: Formulario → Generación de Audio → Video → Storage → Email

---

## Paso 1: Configurar Voz Constante (Papá Noel)

### 1.1 Configurar ElevenLabs con Voz de Papá Noel

**Opción A: Usar voz existente de ElevenLabs**
- Buscar una voz masculina, cálida, apropiada para Papá Noel
- Voice ID recomendado: `21m00Tcm4TlvDq8ikWAM` (Rachel - cambiar por voz masculina)
- O crear una voz personalizada en ElevenLabs

**Opción B: Usar HeyGen con Avatar de Papá Noel**
- Configurar avatar_id específico para Papá Noel
- HeyGen maneja voz y video juntos

**Acción:**
- Agregar variable de entorno `PAPA_NOEL_VOICE_ID` en `.env`
- Actualizar providers para usar esta voz siempre

---

## Paso 2: Verificar Conexión Formulario → API

### 2.1 Verificar API Route Existe
- ✅ Ya existe: `grido_front/src/app/api/generate-video/route.ts`
- Verificar que Redis esté configurado

### 2.2 Probar Formulario Localmente
```bash
cd grido_front
pnpm dev
```
- Llenar formulario
- Verificar que llega a `/api/generate-video`
- Verificar que se encola en Redis

---

## Paso 3: Probar Generación de Audio Local

### 3.1 Script de Prueba de Audio
- Crear `test_audio_generation.py`
- Probar con datos del formulario
- Verificar que se genera audio con voz de Papá Noel
- Verificar formato (WAV, 16kHz, mono)

### 3.2 Verificar Audio Generado
- Reproducir audio generado
- Verificar calidad y voz correcta

---

## Paso 4: Probar Composición de Video Local

### 4.1 Script de Prueba de Video Completo
- Crear `test_video_complete.py`
- Usar videos base (intro, frame3, outro)
- Generar audio con datos del formulario
- Componer video final con FFmpeg
- Verificar resultado local

### 4.2 Verificar Video Generado
- Reproducir video completo
- Verificar que audio está sincronizado
- Verificar calidad y duración

---

## Paso 5: Probar Upload a Firebase Storage

### 5.1 Crear Bucket de Firebase (si no existe)
- Seguir guía en `CREAR_BUCKET_FIREBASE.md`
- Configurar reglas de seguridad

### 5.2 Probar Upload
- Usar `test_storage_only.py` (ya existe)
- Verificar que video se sube correctamente
- Obtener URL pública
- Verificar que URL es accesible

---

## Paso 6: Probar Flujo End-to-End Local

### 6.1 Script de Prueba Completa
- Crear `test_end_to_end.py`
- Simular datos del formulario
- Generar audio → Video → Upload → URL
- Todo en local sin Redis/Modal

### 6.2 Verificar Resultado
- Video generado localmente
- Video subido a Firebase
- URL pública funcional

---

## Paso 7: Conectar con Redis y Worker

### 7.1 Configurar Redis (Upstash)
- Crear cuenta en Upstash
- Obtener `UPSTASH_REDIS_REST_URL` y `UPSTASH_REDIS_REST_TOKEN`
- Configurar en `.env` del frontend

### 7.2 Probar Encolado
- Llenar formulario en landing
- Verificar que se encola en Redis
- Verificar que worker puede leer de la cola

---

## Paso 8: Configurar Email (Resend)

### 8.1 Crear Cuenta Resend
- Crear cuenta en Resend
- Obtener API key
- Verificar dominio (o usar dominio de prueba)

### 8.2 Configurar en Worker
- Agregar `RESEND_API_KEY` en `.env`
- Probar envío de email con URL del video

---

## Paso 9: Prueba Final End-to-End

### 9.1 Flujo Completo
1. Usuario llena formulario en landing
2. Formulario valida contenido
3. Se encola trabajo en Redis
4. Worker procesa:
   - Genera audio con voz de Papá Noel
   - Compone video (intro + frame3 con audio + outro)
   - Sube a Firebase Storage
   - Obtiene URL pública
5. Worker envía email con URL
6. Usuario recibe email

### 9.2 Verificar Todo
- ✅ Video generado correctamente
- ✅ Audio con voz correcta
- ✅ Video en Firebase Storage
- ✅ Email enviado
- ✅ URL funciona

---

## Configuración de Voz Constante

### Variables de Entorno Necesarias:

```bash
# Voz de Papá Noel
PAPA_NOEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # ElevenLabs (cambiar por voz masculina)
PAPA_NOEL_AVATAR_ID=default  # HeyGen (configurar avatar de Papá Noel)

# Providers
ELEVENLABS_API_KEY=xxx
HEYGEN_API_KEY=xxx

# Storage
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# Email
RESEND_API_KEY=re_xxx

# Redis (para producción)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
```

---

## Orden de Ejecución Recomendado

1. ✅ **Paso 1**: Configurar voz constante
2. ✅ **Paso 3**: Probar generación de audio local
3. ✅ **Paso 4**: Probar composición de video local
4. ✅ **Paso 5**: Probar upload a Firebase
5. ✅ **Paso 6**: Probar flujo end-to-end local
6. ⏳ **Paso 2**: Verificar formulario → API
7. ⏳ **Paso 7**: Conectar Redis y Worker
8. ⏳ **Paso 8**: Configurar Email
9. ⏳ **Paso 9**: Prueba final end-to-end

---

## Scripts de Prueba a Crear

- [x] `test_storage_only.py` - Prueba solo storage
- [ ] `test_audio_generation.py` - Prueba generación de audio
- [ ] `test_video_complete.py` - Prueba composición de video
- [ ] `test_end_to_end.py` - Prueba flujo completo local


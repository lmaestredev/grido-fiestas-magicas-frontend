# 🚀 Guía de Prueba - Flujo Completo desde Landing

Esta guía te permite probar el flujo completo: **Landing → Formulario → API → Redis → Worker → Video → Storage**

---

## 📋 Checklist de Configuración

### 1. Variables de Entorno del Worker

Crea/verifica `grido-backend/worker/.env`:

```bash
# Voz de Papá Noel
PAPA_NOEL_VOICE_ID=tu_voice_id  # ElevenLabs
PAPA_NOEL_AVATAR_ID=tu_avatar_id  # HeyGen

# Providers (al menos uno)
ELEVENLABS_API_KEY=xxx
HEYGEN_API_KEY=xxx

# Storage
STORAGE_TYPE=local  # Para pruebas, luego cambiar a firebase
LOCAL_STORAGE_PATH=./storage

# Redis (local o Upstash)
REDIS_URL=redis://localhost:6379  # Local
# O para Upstash:
# REDIS_URL=redis://xxx.upstash.io:6379

# Email (opcional para pruebas)
# RESEND_API_KEY=re_xxx
```

### 2. Variables de Entorno del Frontend

Crea/verifica `grido_front/.env.local`:

```bash
# Redis (Upstash)
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx

# API Secret
VIDEO_API_SECRET=tu_secret_aqui

# Content Moderation
PERSPECTIVE_API_KEY=xxx
```

### 3. Assets Requeridos

Verifica que existan en `grido-backend/worker/assets/`:
- ✅ `Frames_1_2_to_3.mov` (intro)
- ✅ `frame3_santa_base.mp4` (frame 3 - puede ser corto para pruebas)
- ✅ `Frame_4_NocheMagica.mov` (outro)

---

## 🧪 Opción 1: Prueba Local Completa (Sin Landing)

### Paso 1: Iniciar Redis Local (si no tienes Upstash)

```bash
# macOS
brew install redis
brew services start redis

# O ejecutar manualmente
redis-server
```

### Paso 2: Ejecutar Prueba Completa

```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_flujo_completo_landing.py
```

Este script:
1. ✅ Simula el envío del formulario
2. ✅ Encola trabajo en Redis
3. ✅ Procesa el video con el worker
4. ✅ Verifica el resultado

---

## 🌐 Opción 2: Prueba con Landing Real

### Paso 1: Iniciar Frontend

```bash
cd grido_front
pnpm install
pnpm dev
```

### Paso 2: Iniciar Worker (en otra terminal)

```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

El worker estará escuchando trabajos de Redis.

### Paso 3: Llenar Formulario en Landing

1. Abre `http://localhost:3000`
2. Llena el formulario con datos de prueba
3. Envía el formulario

### Paso 4: Verificar Procesamiento

**En la terminal del worker verás:**
```
[WORKER] Worker iniciado, esperando trabajos...
[video_id] Iniciando procesamiento...
[video_id] Generando audio...
[video_id] Componiendo video...
[video_id] Subiendo video...
[video_id] Procesamiento completado exitosamente
```

**En la landing verás:**
- Mensaje de éxito: "¡Tu saludo mágico se está generando! Te llegará por email en unos minutos. 🎄✨"

---

## 🔍 Verificar Resultado

### Opción A: Verificar en Redis

```bash
redis-cli
> GET job:video_id_aqui
> LRANGE video:queue 0 -1
```

### Opción B: Verificar Archivo Local

Si usas `STORAGE_TYPE=local`:
```bash
cd grido-backend/worker/storage
ls -lh
# Verás el video generado
```

### Opción C: Verificar en Firebase

Si usas `STORAGE_TYPE=firebase`:
1. Ve a Firebase Console → Storage
2. Busca en la carpeta `videos/`
3. Verifica que el video esté ahí

---

## 🐛 Solución de Problemas

### Error: "No se puede conectar a Redis"
- Verifica que Redis esté corriendo: `redis-cli ping`
- Verifica `REDIS_URL` en `.env`
- Si usas Upstash, verifica credenciales

### Error: "No hay providers disponibles"
- Verifica que tengas al menos una API key:
  - `ELEVENLABS_API_KEY` o
  - `HEYGEN_API_KEY`

### Error: "Video se corta"
- El frame3 tiene duración corta (~5.2 seg)
- Funciona para pruebas, pero para producción necesitas 15-20 seg
- El video se cortará si el diálogo es más largo

### Error: "Storage falla"
- Si usas Firebase, verifica que el bucket exista
- Si usas local, verifica permisos de escritura
- Verifica `STORAGE_TYPE` en `.env`

---

## 📊 Flujo Completo Esperado

```
1. Usuario llena formulario en landing
   ↓
2. Formulario valida contenido (Perspective API)
   ↓
3. Frontend llama a /api/generate-video
   ↓
4. API encola trabajo en Redis
   ↓
5. Worker lee de Redis (brpop)
   ↓
6. Worker procesa:
   - Genera audio (ElevenLabs o HeyGen)
   - Compone video (intro + frame3 + outro)
   - Sube a storage (Firebase/Local)
   ↓
7. Worker envía email (si está configurado)
   ↓
8. Worker actualiza estado en Redis (completed)
   ↓
9. Usuario recibe email con URL del video
```

---

## ✅ Checklist de Prueba

- [ ] Redis configurado y funcionando
- [ ] Variables de entorno configuradas
- [ ] Assets en lugar correcto
- [ ] Al menos un provider configurado (ElevenLabs o HeyGen)
- [ ] Storage configurado (local o Firebase)
- [ ] Worker corriendo y escuchando
- [ ] Frontend corriendo
- [ ] Formulario envía datos correctamente
- [ ] Worker procesa el video
- [ ] Video se genera correctamente
- [ ] Video se sube a storage
- [ ] URL pública funciona

---

## 🎯 Próximos Pasos

Una vez que el flujo completo funcione:

1. ✅ Configurar email (Resend)
2. ✅ Mejorar frame3 (resolución y duración)
3. ✅ Optimizar calidad de video
4. ✅ Deploy a producción (Modal + Vercel)


# 🚀 Comandos para Probar

## ⚠️ Antes de Probar

Asegúrate de tener `ELEVENLABS_API_KEY` en `grido-backend/worker/.env`:

```bash
ELEVENLABS_API_KEY=tu_api_key_aqui
```

---

## Opción 1: Prueba Sin Redis (Más Rápida)

### Paso 1: Verificar Configuración
```bash
cd grido-backend/worker
source venv/bin/activate
python3 verificar_config.py
```

### Paso 2: Probar Generación de Audio
```bash
python3 test_audio_generation.py
```

### Paso 3: Probar Flujo Completo
```bash
STORAGE_TYPE=local python3 test_flujo_sin_redis.py
```

**Esto probará:**
- ✅ Generación de audio con ElevenLabs
- ✅ Composición de video
- ✅ Upload a storage local
- ✅ Verificación del resultado

---

## Opción 2: Prueba Con Redis (Más Realista)

### Paso 1: Instalar Redis
```bash
brew install redis
brew services start redis

# Verificar
redis-cli ping  # Debe responder: PONG
```

### Paso 2: Encolar Trabajo (Terminal 1)
```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_simular_landing.py
```

### Paso 3: Procesar (Terminal 2)
```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

**Esto probará:**
- ✅ Formulario → API → Redis
- ✅ Worker leyendo de Redis
- ✅ Procesamiento completo
- ✅ Actualización de estado en Redis

---

## Opción 3: Prueba Con Landing Real

### Paso 1: Configurar Frontend
```bash
cd grido_front
# Verificar .env.local tiene:
# UPSTASH_REDIS_REST_URL
# UPSTASH_REDIS_REST_TOKEN
# VIDEO_API_SECRET
# PERSPECTIVE_API_KEY
```

### Paso 2: Iniciar Frontend (Terminal 1)
```bash
cd grido_front
pnpm dev
```

### Paso 3: Iniciar Worker (Terminal 2)
```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

### Paso 4: Probar
1. Abre `http://localhost:3000`
2. Llena el formulario
3. Envía
4. Verifica logs en ambas terminales

---

## Verificar Resultado

### Si usas Storage Local:
```bash
cd grido-backend/worker/storage
ls -lh
# Verás el video generado
```

### Si usas Firebase:
1. Ve a Firebase Console → Storage
2. Busca en carpeta `videos/`
3. Verifica que el video esté ahí

### Verificar en Redis:
```bash
redis-cli
> LRANGE video:queue 0 -1
> GET job:video_id_aqui
```

---

## Solución de Problemas

**"No TTS providers available"**
- Verifica `ELEVENLABS_API_KEY` en `.env`
- Ejecuta `python3 verificar_config.py`

**"Redis connection refused"**
- Inicia Redis: `brew services start redis`
- O configura Upstash Redis

**"Video se corta"**
- Normal con frame3 corto (~5.2 seg)
- Funciona para pruebas
- Para producción, re-exporta frame3 más largo


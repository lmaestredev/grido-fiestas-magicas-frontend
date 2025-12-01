# 🚀 Inicio Rápido - Flujo Completo

## Configuración Mínima para Probar

### 1. Configurar Variables de Entorno

**Backend (`grido-backend/worker/.env`):**
```bash
# Provider (al menos uno)
ELEVENLABS_API_KEY=xxx
# O
HEYGEN_API_KEY=xxx

# Voz constante
PAPA_NOEL_VOICE_ID=tu_voice_id  # Si usas ElevenLabs

# Storage (local para pruebas)
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage

# Redis (local)
REDIS_URL=redis://localhost:6379
```

**Frontend (`grido_front/.env.local`):**
```bash
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
VIDEO_API_SECRET=tu_secret_aqui
PERSPECTIVE_API_KEY=xxx
```

### 2. Iniciar Redis (si no tienes Upstash)

```bash
# macOS
brew install redis
brew services start redis

# Verificar
redis-cli ping  # Debe responder: PONG
```

### 3. Probar Flujo Completo

**Opción A: Prueba Automática (Todo en uno)**
```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_flujo_completo_landing.py
```

**Opción B: Prueba Manual (2 terminales)**

Terminal 1 - Encolar trabajo:
```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_simular_landing.py
```

Terminal 2 - Procesar:
```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

**Opción C: Con Landing Real**

Terminal 1 - Frontend:
```bash
cd grido_front
pnpm dev
```

Terminal 2 - Worker:
```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

Luego llena el formulario en `http://localhost:3000`

---

## ✅ Verificar que Funciona

1. **Worker procesa el video:**
   - Verás logs en la terminal del worker
   - Video generado en `./storage/` (si usas local)

2. **Verificar resultado:**
   ```bash
   cd grido-backend/worker/storage
   ls -lh
   # Verás el video generado
   ```

3. **Verificar en Redis:**
   ```bash
   redis-cli
   > GET job:video_id_aqui
   > LRANGE video:queue 0 -1
   ```

---

## 🎯 Flujo Esperado

```
Landing → Formulario → API → Redis → Worker → Video → Storage
```

1. ✅ Formulario envía datos
2. ✅ API encola en Redis
3. ✅ Worker lee de Redis
4. ✅ Worker genera audio (ElevenLabs/HeyGen)
5. ✅ Worker compone video
6. ✅ Worker sube a storage
7. ✅ Worker actualiza estado

---

## 📝 Notas Importantes

- **Frame3 corto:** El video puede cortarse si el diálogo es largo (frame3 tiene ~5.2 seg)
- **Funciona para pruebas:** Aunque se corte, puedes verificar el flujo completo
- **Para producción:** Necesitas re-exportar frame3 en resolución correcta y duración adecuada

---

## 🐛 Problemas Comunes

**"No se puede conectar a Redis"**
- Inicia Redis: `brew services start redis`
- O configura Upstash Redis

**"No hay providers disponibles"**
- Configura `ELEVENLABS_API_KEY` o `HEYGEN_API_KEY`

**"Video se corta"**
- Normal con frame3 corto, funciona para pruebas


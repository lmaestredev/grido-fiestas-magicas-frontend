# Estado Actual - Pruebas del Flujo Completo

## ✅ Lo que está listo

1. **Assets configurados:**
   - ✅ `Frames_1_2_to_3.mov` (intro)
   - ✅ `frame3_santa_base.mp4` (frame 3 - corto pero funcional)
   - ✅ `Frame_4_NocheMagica.mov` (outro)

2. **Storage configurado:**
   - ✅ Local funcionando
   - ✅ Firebase configurado (falta crear bucket)

3. **Código listo:**
   - ✅ Formulario → API → Redis
   - ✅ Worker → Procesamiento → Storage
   - ✅ Voz constante configurada

4. **Scripts de prueba:**
   - ✅ `test_end_to_end.py` - Prueba completa sin Redis
   - ✅ `test_flujo_sin_redis.py` - Flujo directo
   - ✅ `test_simular_landing.py` - Simula landing
   - ✅ `test_flujo_completo_landing.py` - Flujo completo con Redis

---

## ⚠️ Problemas Encontrados

### 1. HeyGen API - Endpoint 404

**Problema:** Todos los endpoints de HeyGen devuelven 404
- `https://api.heygen.com/v2/video.generate` ❌
- `https://api.heygen.com/v2/video/talking_photo` ❌
- `https://api.heygen.com/v1/video.generate` ❌

**Solución temporal:** Usar ElevenLabs para TTS

**Solución definitiva:** Buscar documentación correcta de HeyGen o usar SDK oficial

### 2. Redis no instalado

**Problema:** Redis no está instalado localmente

**Soluciones:**
- **Opción A:** Instalar Redis local: `brew install redis && brew services start redis`
- **Opción B:** Usar Upstash Redis (cloud, más fácil)
- **Opción C:** Probar sin Redis usando `test_flujo_sin_redis.py`

### 3. ElevenLabs no configurado

**Problema:** No hay API key de ElevenLabs configurada

**Solución:** Agregar `ELEVENLABS_API_KEY` en `.env`

---

## 🚀 Próximos Pasos para Probar

### Opción 1: Prueba Sin Redis (Más Rápido)

```bash
cd grido-backend/worker
source venv/bin/activate

# Configurar ElevenLabs (necesario)
# Agregar ELEVENLABS_API_KEY=xxx en .env

# Ejecutar prueba
STORAGE_TYPE=local python3 test_flujo_sin_redis.py
```

**Ventajas:**
- ✅ No requiere Redis
- ✅ Prueba todo el flujo
- ✅ Más rápido

**Desventajas:**
- ⚠️ No prueba la cola Redis
- ⚠️ No prueba el worker escuchando

### Opción 2: Prueba Con Redis (Más Realista)

**Paso 1:** Instalar Redis
```bash
brew install redis
brew services start redis
```

**Paso 2:** Configurar
```bash
# En .env ya está:
REDIS_URL=redis://localhost:6379
```

**Paso 3:** Probar
```bash
# Terminal 1: Encolar trabajo
python3 test_simular_landing.py

# Terminal 2: Procesar
python3 video-worker.py
```

### Opción 3: Prueba Con Landing Real

**Paso 1:** Configurar Redis (ver Opción 2)

**Paso 2:** Iniciar Frontend
```bash
cd grido_front
pnpm dev
```

**Paso 3:** Iniciar Worker
```bash
cd grido-backend/worker
source venv/bin/activate
python3 video-worker.py
```

**Paso 4:** Llenar formulario en `http://localhost:3000`

---

## 📋 Checklist para Probar

### Para Opción 1 (Sin Redis):
- [ ] Configurar `ELEVENLABS_API_KEY` en `.env`
- [ ] Configurar `STORAGE_TYPE=local`
- [ ] Ejecutar `test_flujo_sin_redis.py`

### Para Opción 2 (Con Redis):
- [ ] Instalar Redis: `brew install redis`
- [ ] Iniciar Redis: `brew services start redis`
- [ ] Configurar `ELEVENLABS_API_KEY` o `HEYGEN_API_KEY`
- [ ] Ejecutar `test_simular_landing.py` + `video-worker.py`

### Para Opción 3 (Con Landing):
- [ ] Todo de Opción 2
- [ ] Configurar variables de entorno del frontend
- [ ] Iniciar frontend y worker
- [ ] Llenar formulario

---

## 🔧 Configuración Mínima Necesaria

**Backend (`.env`):**
```bash
# Provider (al menos uno)
ELEVENLABS_API_KEY=xxx  # Recomendado para pruebas
# O
HEYGEN_API_KEY=xxx  # Tiene problemas de endpoint

# Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage

# Redis (solo para Opción 2 y 3)
REDIS_URL=redis://localhost:6379
```

**Frontend (`.env.local`):**
```bash
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
VIDEO_API_SECRET=tu_secret
PERSPECTIVE_API_KEY=xxx
```

---

## 💡 Recomendación

**Para probar AHORA (más rápido):**
1. Configurar `ELEVENLABS_API_KEY`
2. Usar `test_flujo_sin_redis.py`
3. Verificar que el video se genera

**Para probar COMPLETO (más realista):**
1. Instalar Redis
2. Configurar ElevenLabs
3. Probar con landing real


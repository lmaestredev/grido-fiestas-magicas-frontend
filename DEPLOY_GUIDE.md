# Guía Completa de Deploy - Grido Fiestas Mágicas

## Tabla de Contenidos
1. [Qué Cargar y Dónde](#qué-cargar-y-dónde)
2. [Proceso de Deploy](#proceso-de-deploy)
3. [Pruebas del Flujo Completo](#pruebas-del-flujo-completo)

---

## Qué Cargar y Dónde

### 1. Videos Base (Assets)

**Ubicación:** `grido-backend/assets/`

**Archivos requeridos:**
- `intro_frames1_2.mp4` - Intro + Pote vacío (sin audio, 5-7 seg)
- `frame3_santa_base.mp4` - Papá Noel estático (sin audio, ~15 seg)
- `outro_frame4.mp4` - Cierre (sin audio, 3-5 seg)

**Especificaciones técnicas:**
- Resolución: 1080x1920 (vertical)
- FPS: 25
- Codec: H.264
- Formato: MP4
- Sin audio (o audio que será reemplazado)

**Cómo cargar:**
```bash
# Desde tu computadora
cd grido-backend/assets/
# Copiar los 3 archivos MP4 aquí
```

**Para Modal (deploy):**
Los assets deben estar en un NetworkFileSystem de Modal. Opciones:
1. **Opción A - Montar desde local:** Los assets se copian automáticamente cuando haces deploy
2. **Opción B - Subir manualmente:** Usar `modal volume` para crear un volumen persistente

```bash
# Crear volumen persistente en Modal
modal volume create grido-assets

# Subir assets (desde Modal CLI o dashboard)
# Los assets estarán disponibles en /assets/ dentro del worker
```

---

### 2. API Keys y Credenciales

#### 2.1 Upstash Redis

**Dónde obtener:**
1. Ir a https://console.upstash.com
2. Crear nueva base de datos Redis
3. Copiar:
   - `UPSTASH_REDIS_REST_URL` (ej: `https://xxx.upstash.io`)
   - `UPSTASH_REDIS_REST_TOKEN` (token de autenticación)

**Dónde configurar:**
- **Vercel (Frontend):** Variables de entorno en dashboard
- **Modal (Worker):** Secreto `grido-secrets`

---

#### 2.2 Cloudflare R2 (Storage)

**Dónde obtener:**
1. Ir a https://dash.cloudflare.com
2. R2 → Create bucket → `grido-papa-noel-videos`
3. Settings → Manage R2 API Tokens → Create API Token
4. Copiar:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ENDPOINT_URL` (ej: `https://xxx.r2.cloudflarestorage.com`)

**Dónde configurar:**
- **Modal (Worker):** Secreto `grido-secrets`

**Configuración adicional:**
- Habilitar dominio público para el bucket
- Configurar CORS si es necesario

---

#### 2.3 Resend (Email)

**Dónde obtener:**
1. Ir a https://resend.com
2. API Keys → Create API Key
3. Copiar `RESEND_API_KEY`

**Dónde configurar:**
- **Modal (Worker):** Secreto `grido-secrets`

**Configuración adicional:**
- Verificar dominio de envío (o usar dominio de prueba)
- Configurar "from" address en el código

---

#### 2.4 ElevenLabs (TTS Fallback) - Opcional

**Dónde obtener:**
1. Ir a https://elevenlabs.io
2. Profile → API Key
3. Copiar `ELEVENLABS_API_KEY`

**Dónde configurar:**
- **Modal (Worker):** Secreto `grido-secrets`

**Nota:** Se usa como fallback si Kokoro TTS no está disponible.

---

#### 2.5 HeyGen (Video Completo Fallback) - Opcional

**Dónde obtener:**
1. Ir a https://heygen.com
2. Settings → API
3. Create API Key
4. Copiar `HEYGEN_API_KEY`

**Dónde configurar:**
- **Modal (Worker):** Secreto `grido-secrets`

**Nota:** Se usa como último recurso si TTS + lip-sync fallan.

---

#### 2.6 Kokoro TTS (Local GPU) - Opcional

**Dónde obtener:**
- Instalar Kokoro localmente o en Modal
- Si tienes modelo pre-entrenado, especificar ruta

**Dónde configurar:**
- **Modal (Worker):** Variables de entorno en secreto:
  - `KOKORO_MODEL_PATH` (opcional)
  - `KOKORO_SCRIPT_PATH` (opcional)

**Nota:** Requiere instalación en la imagen de Docker de Modal.

---

#### 2.7 MuseTalk (Local GPU) - Opcional

**Dónde obtener:**
- Instalar MuseTalk localmente o en Modal
- Si tienes modelo pre-entrenado, especificar ruta

**Dónde configurar:**
- **Modal (Worker):** Variables de entorno en secreto:
  - `MUSETALK_MODEL_PATH` (opcional)
  - `MUSETALK_SCRIPT_PATH` (opcional)

**Nota:** Requiere instalación en la imagen de Docker de Modal.

---

### 3. Variables de Entorno - Resumen

#### Frontend (Vercel)
```
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
VIDEO_API_SECRET=tu-secreto-aqui
VIDEO_API_URL=/api/generate-video  (o URL completa si es externa)
```

#### Worker (Modal - Secreto `grido-secrets`)
```
# Redis
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=xxx
REDIS_URL=redis://default:xxx@xxx.upstash.io:6379

# Cloudflare R2
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
S3_BUCKET=grido-papa-noel-videos
AWS_REGION=auto

# Resend
RESEND_API_KEY=re_xxx

# ElevenLabs (opcional)
ELEVENLABS_API_KEY=xxx

# HeyGen (opcional)
HEYGEN_API_KEY=xxx

# Kokoro (opcional)
KOKORO_MODEL_PATH=/path/to/model
KOKORO_SCRIPT_PATH=kokoro/infer.py

# MuseTalk (opcional)
MUSETALK_MODEL_PATH=/path/to/model
MUSETALK_SCRIPT_PATH=musetalk/realtime_inference.py
```

---

## Proceso de Deploy

### Paso 1: Preparar Repositorio

```bash
# Asegúrate de que todo esté commiteado
git status

# Push a GitHub (si no lo has hecho)
git push origin main
```

---

### Paso 2: Deploy del Frontend (Vercel)

#### 2.1 Crear Proyecto en Vercel

1. Ir a https://vercel.com
2. New Project → Import Git Repository
3. Seleccionar tu repositorio de GitHub
4. **Configuración importante:**
   - **Root Directory:** `grido_front`
   - **Framework Preset:** Next.js
   - **Build Command:** `pnpm build` (o `npm run build`)
   - **Output Directory:** `.next`

#### 2.2 Configurar Variables de Entorno

En Vercel Dashboard → Settings → Environment Variables:

```
UPSTASH_REDIS_REST_URL = https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN = xxx
VIDEO_API_SECRET = tu-secreto-seguro-aqui
```

#### 2.3 Deploy

- Vercel hace deploy automático al hacer push a `main`
- O manualmente: Dashboard → Deployments → Redeploy

#### 2.4 Verificar Deploy

```bash
# Verificar que la API route funciona
curl -X POST https://tu-app.vercel.app/api/generate-video \
  -H "Authorization: Bearer tu-secreto-seguro-aqui" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Test","email":"test@test.com","provincia":"Buenos Aires","queHizo":"Test","recuerdoEspecial":"Test","pedidoNocheMagica":"Test","parentesco":"Test"}'
```

---

### Paso 3: Configurar Modal

#### 3.1 Instalar Modal CLI

```bash
pip install modal
```

#### 3.2 Autenticar

```bash
modal token new
# Sigue las instrucciones en el navegador
```

#### 3.3 Crear Secreto con Variables de Entorno

```bash
# Opción A: Desde CLI
modal secret create grido-secrets \
  UPSTASH_REDIS_REST_URL=https://xxx.upstash.io \
  UPSTASH_REDIS_REST_TOKEN=xxx \
  REDIS_URL=redis://default:xxx@xxx.upstash.io:6379 \
  AWS_ACCESS_KEY_ID=xxx \
  AWS_SECRET_ACCESS_KEY=xxx \
  AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com \
  S3_BUCKET=grido-papa-noel-videos \
  RESEND_API_KEY=re_xxx \
  ELEVENLABS_API_KEY=xxx \
  HEYGEN_API_KEY=xxx

# Opción B: Desde Dashboard
# Ir a https://modal.com/secrets → Create Secret → grido-secrets
# Agregar todas las variables manualmente
```

#### 3.4 Preparar Assets en Modal

**Opción A - NetworkFileSystem (Recomendado):**

```bash
# Crear volumen persistente
modal volume create grido-assets

# Subir assets (desde Modal dashboard o CLI)
# Los assets estarán en /assets/ dentro del worker
```

**Opción B - Montar desde código:**

Los assets se copian automáticamente si están en `grido-backend/assets/` y usas `.copy_local_dir()` en la imagen de Modal.

#### 3.5 Deploy del Worker

```bash
cd grido-backend/worker
modal deploy modal_worker.py
```

**Verificar deploy:**
```bash
# Ver logs
modal logs grido-video-worker

# Ver estado
modal app list
```

---

### Paso 4: Configurar Worker Local (Opcional - Para desarrollo)

Si quieres correr el worker localmente en lugar de Modal:

```bash
cd grido-backend/worker

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp ../.env.example .env
# Editar .env con tus credenciales

# Correr worker
python video-worker.py
```

---

## Pruebas del Flujo Completo

### Prueba 1: Verificar Configuración de Servicios

#### 1.1 Test de Redis (Upstash)

```bash
# Desde terminal o script Python
python -c "
import os
from upstash_redis import Redis

redis = Redis(
    url=os.getenv('UPSTASH_REDIS_REST_URL'),
    token=os.getenv('UPSTASH_REDIS_REST_TOKEN')
)

# Test write
redis.set('test', 'value')
print('✅ Redis write OK')

# Test read
value = redis.get('test')
print(f'✅ Redis read OK: {value}')
"
```

#### 1.2 Test de Cloudflare R2

```bash
python -c "
import boto3
import os

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='auto'
)

# Test list buckets
buckets = s3.list_buckets()
print('✅ R2 connection OK')
print(f'Buckets: {[b[\"Name\"] for b in buckets[\"Buckets\"]]}')
"
```

#### 1.3 Test de Resend

```bash
python -c "
import requests
import os

response = requests.post(
    'https://api.resend.com/emails',
    headers={
        'Authorization': f'Bearer {os.getenv(\"RESEND_API_KEY\")}',
        'Content-Type': 'application/json'
    },
    json={
        'from': 'test@example.com',
        'to': ['tu-email@example.com'],
        'subject': 'Test',
        'text': 'Test email'
    }
)
print(f'✅ Resend test: {response.status_code}')
"
```

#### 1.4 Test de ElevenLabs (si configurado)

```bash
python -c "
import requests
import os

response = requests.post(
    f'https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM',
    headers={
        'xi-api-key': os.getenv('ELEVENLABS_API_KEY'),
        'Content-Type': 'application/json'
    },
    json={'text': 'Test'}
)
print(f'✅ ElevenLabs test: {response.status_code}')
"
```

#### 1.5 Test de HeyGen (si configurado)

```bash
python -c "
import requests
import os

response = requests.get(
    'https://api.heygen.com/v1/avatars',
    headers={'X-Api-Key': os.getenv('HEYGEN_API_KEY')}
)
print(f'✅ HeyGen test: {response.status_code}')
"
```

---

### Prueba 2: Test de Proveedores Individuales

```bash
cd grido-backend/worker

# Configurar variables de entorno
export $(cat ../.env.example | grep -v '^#' | xargs)

# Ejecutar test de proveedores
python test_providers.py
```

**Qué verificar:**
- ✅ Kokoro TTS genera audio (si disponible)
- ✅ ElevenLabs TTS genera audio (si configurado)
- ✅ MuseTalk aplica lip-sync (si disponible)
- ✅ HeyGen genera video completo (si configurado)
- ✅ ProviderManager detecta proveedores disponibles

---

### Prueba 3: Test End-to-End Completo

#### 3.1 Test desde Frontend (Formulario)

1. **Abrir landing page:**
   ```
   https://tu-app.vercel.app
   ```

2. **Llenar formulario con datos de prueba:**
   - Nombre: "Juan"
   - Parentesco: "Papá"
   - Email: "tu-email@example.com"
   - Provincia: "Buenos Aires"
   - Que hizo: "Fue un gran año, estudió mucho y ayudó en casa"
   - Recuerdo especial: "Recuerdo cuando fuimos al parque juntos"
   - Pedido noche mágica: "Quiere una bicicleta nueva"

3. **Enviar formulario**

4. **Verificar:**
   - ✅ Mensaje de éxito aparece
   - ✅ Video ID se muestra (opcional)
   - ✅ No hay errores en consola del navegador

#### 3.2 Verificar en Redis (Job creado)

```bash
python -c "
import os
from upstash_redis import Redis

redis = Redis(
    url=os.getenv('UPSTASH_REDIS_REST_URL'),
    token=os.getenv('UPSTASH_REDIS_REST_TOKEN')
)

# Ver cola
queue_length = redis.llen('video:queue')
print(f'Jobs en cola: {queue_length}')

# Ver último job (si hay)
if queue_length > 0:
    last_job_id = redis.lindex('video:queue', 0)
    job_data = redis.get(f'job:{last_job_id}')
    print(f'Último job: {job_data}')
"
```

#### 3.3 Verificar Worker Procesando

**Si usas Modal:**
```bash
# Ver logs en tiempo real
modal logs grido-video-worker --follow

# Ver logs de un job específico
modal logs grido-video-worker | grep "video_id_aqui"
```

**Si usas worker local:**
```bash
# Los logs aparecen en la terminal donde corre el worker
cd grido-backend/worker
python video-worker.py
```

**Qué buscar en logs:**
- ✅ "Iniciando procesamiento..."
- ✅ "Generando audio con [Provider]"
- ✅ "Aplicando lip-sync con [Provider]"
- ✅ "Video subido: [URL]"
- ✅ "Email enviado"
- ✅ "✅ Completado"

#### 3.4 Verificar Video en R2

```bash
python -c "
import boto3
import os

s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='auto'
)

# Listar videos
objects = s3.list_objects_v2(Bucket=os.getenv('S3_BUCKET'), Prefix='videos/')
if 'Contents' in objects:
    for obj in objects['Contents']:
        print(f'✅ Video: {obj[\"Key\"]} ({obj[\"Size\"]} bytes)')
else:
    print('No hay videos aún')
"
```

#### 3.5 Verificar Email Recibido

- ✅ Revisar inbox del email usado en el formulario
- ✅ Verificar que el email contiene link al video
- ✅ Hacer clic en el link y verificar que el video se reproduce

---

### Prueba 4: Test de Fallback

#### 4.1 Test Fallback TTS

**Deshabilitar Kokoro:**
```bash
# En Modal secrets o .env
DISABLE_KOKORO=true
```

**Enviar formulario y verificar:**
- ✅ Logs muestran que usa ElevenLabs en lugar de Kokoro
- ✅ Video se genera correctamente

#### 4.2 Test Fallback Completo (HeyGen)

**Deshabilitar Kokoro y MuseTalk:**
```bash
DISABLE_KOKORO=true
DISABLE_MUSETALK=true
```

**Enviar formulario y verificar:**
- ✅ Logs muestran que usa HeyGen
- ✅ Video se genera correctamente (puede tardar más)

---

### Prueba 5: Test de Errores y Recuperación

#### 5.1 Test con API Key Inválida

**Temporalmente cambiar API key de ElevenLabs a inválida:**
- ✅ Sistema debe fallar a ElevenLabs
- ✅ Debe intentar siguiente proveedor o fallback a HeyGen

#### 5.2 Test con Redis Desconectado

**Temporalmente cambiar URL de Redis:**
- ✅ Frontend debe mostrar error al usuario
- ✅ No debe crear job en Redis

#### 5.3 Test con R2 Inaccesible

**Temporalmente cambiar credenciales de R2:**
- ✅ Worker debe fallar al subir video
- ✅ Debe registrar error en Redis
- ✅ No debe enviar email

---

### Checklist Final de Pruebas

- [ ] **Configuración:**
  - [ ] Redis conecta correctamente
  - [ ] R2 conecta correctamente
  - [ ] Resend envía emails
  - [ ] ElevenLabs funciona (si configurado)
  - [ ] HeyGen funciona (si configurado)

- [ ] **Flujo Completo:**
  - [ ] Formulario envía correctamente
  - [ ] Job se crea en Redis
  - [ ] Worker procesa el job
  - [ ] Video se genera (con cualquier proveedor disponible)
  - [ ] Video se sube a R2
  - [ ] Email se envía con link
  - [ ] Video se reproduce correctamente

- [ ] **Fallback:**
  - [ ] Fallback TTS funciona
  - [ ] Fallback completo (HeyGen) funciona

- [ ] **Errores:**
  - [ ] Errores se manejan correctamente
  - [ ] Logs son claros y útiles
  - [ ] Usuario recibe feedback apropiado

---

## Troubleshooting Común

### El video no se genera

1. **Verificar logs del worker:**
   ```bash
   modal logs grido-video-worker --follow
   ```

2. **Verificar que hay jobs en la cola:**
   ```bash
   # Verificar Redis
   redis-cli -u $REDIS_URL LLEN video:queue
   ```

3. **Verificar que los assets existen:**
   ```bash
   # En Modal
   modal run modal_worker.py -- ls /assets
   ```

### El email no llega

1. **Verificar Resend:**
   - Revisar dashboard de Resend para ver logs
   - Verificar que el dominio está verificado
   - Revisar spam

2. **Verificar logs:**
   ```bash
   modal logs grido-video-worker | grep "Email"
   ```

### Error de GPU en Modal

1. **Verificar créditos:**
   - Ir a Modal dashboard → Billing
   - Asegurarse de tener créditos

2. **Probar GPU más pequeña:**
   ```python
   # En modal_worker.py, cambiar:
   gpu="T4"  # En lugar de "A10G"
   ```

### Proveedores no disponibles

1. **Verificar variables de entorno:**
   ```bash
   modal secret list grido-secrets
   ```

2. **Ejecutar test de proveedores:**
   ```bash
   python test_providers.py
   ```

---

## Próximos Pasos Post-Deploy

1. **Monitoreo:**
   - Configurar alertas en Modal para errores
   - Monitorear costos de APIs externas
   - Revisar logs regularmente

2. **Optimización:**
   - Ajustar orden de fallback según performance/costo
   - Optimizar tiempos de procesamiento
   - Implementar caching si es necesario

3. **Mejoras:**
   - Página de estado del video
   - Analytics y métricas
   - Rate limiting
   - Retry logic mejorado


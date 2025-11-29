# Guía Rápida de Setup - Grido Fiestas Mágicas

## 1. Preparar Assets (5 minutos)

Exporta estos 3 videos desde tu archivo de diseño:

```
assets/
├── intro_frames1_2.mp4      # Intro + Pote vacío (sin audio)
├── frame3_santa_base.mp4     # Papá Noel base (sin audio)
└── outro_frame4.mp4          # Cierre (sin audio)
```

**Specs:** 1080x1920, 25fps, H.264, MP4

## 2. Crear Cuentas (10 minutos)

1. **Vercel:** https://vercel.com/signup
2. **Modal:** https://modal.com/signup
3. **Upstash:** https://console.upstash.com/register
4. **Cloudflare:** https://dash.cloudflare.com/sign-up
5. **Resend:** https://resend.com/signup
6. **ElevenLabs:** https://elevenlabs.io (opcional, para TTS fallback)
7. **HeyGen:** https://heygen.com (opcional, para video completo fallback)

## 3. Configurar Servicios (15 minutos)

### Upstash Redis

1. Crear base de datos Redis
2. Copiar `UPSTASH_REDIS_REST_URL` y `UPSTASH_REDIS_REST_TOKEN`

### Cloudflare R2

1. Crear bucket: `grido-papa-noel-videos`
2. Crear API token con permisos de lectura/escritura
3. Copiar `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL`
4. Configurar dominio público para el bucket

### Resend

1. Verificar dominio (o usar dominio de prueba)
2. Crear API key
3. Copiar `RESEND_API_KEY`

### ElevenLabs (Opcional - TTS Fallback)

1. Crear cuenta en https://elevenlabs.io
2. Ir a Profile → API Key
3. Copiar `ELEVENLABS_API_KEY`
4. Nota: Se usa como fallback si Kokoro TTS no está disponible

### HeyGen (Opcional - Video Completo Fallback)

1. Crear cuenta en https://heygen.com
2. Ir a Settings → API
3. Crear API key
4. Copiar `HEYGEN_API_KEY`
5. Nota: Se usa como último recurso si TTS + lip-sync fallan

### Modal

1. Instalar CLI: `pip install modal`
2. Autenticar: `modal token new`
3. Crear secreto `grido-secrets` con todas las variables de entorno:
   - Redis (Upstash)
   - Cloudflare R2
   - Resend
   - ElevenLabs (opcional)
   - HeyGen (opcional)

## 4. Deploy del Worker (5 minutos)

```bash
cd grido-backend/worker
modal deploy modal_worker.py
```

Esto subirá tu worker a Modal y lo dejará corriendo.

## 5. Deploy del Frontend (5 minutos)

1. Sube tu código a GitHub
2. Importa el repo en Vercel
3. Configura variables de entorno en Vercel:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
   - `VIDEO_API_SECRET`

4. Deploy automático

## 6. Prueba (2 minutos)

1. Abre tu landing en la URL de Vercel
2. Llena el formulario
3. Espera ~30 segundos
4. Revisa tu email

## Troubleshooting

**El video no llega:**
- Revisa logs en Modal: `modal logs grido-video-worker`
- Revisa logs en Vercel: Dashboard → Functions
- Verifica que Redis tenga trabajos: `redis-cli -u $REDIS_URL llen video:queue`

**Error de GPU:**
- Verifica que tu cuenta de Modal tenga créditos
- Prueba con GPU más pequeña: `gpu="T4"`

**Email no llega:**
- Verifica dominio en Resend
- Revisa spam
- Usa email de prueba de Resend

## Costos Estimados

- **Setup:** $0
- **Testing (10 videos):** ~$0.01
- **Producción (1000 videos):** ~$2-5

## Sistema de Proveedores con Fallback

El sistema implementa un fallback automático entre múltiples proveedores:

1. **TTS Principal**: Kokoro TTS (local/GPU)
2. **TTS Fallback**: ElevenLabs API
3. **Lip-sync Principal**: MuseTalk (local/GPU)
4. **Fallback Completo**: HeyGen API (TTS + lip-sync en un solo paso)

### Flujo de Procesamiento

```
Intento 1: Kokoro TTS → MuseTalk lip-sync
  ↓ (si falla)
Intento 2: ElevenLabs TTS → MuseTalk lip-sync
  ↓ (si falla)
Intento 3: HeyGen API (video completo)
```

### Deshabilitar Proveedores

Puedes deshabilitar proveedores específicos usando variables de entorno:
- `DISABLE_KOKORO=true`
- `DISABLE_ELEVENLABS=true`
- `DISABLE_MUSETALK=true`
- `DISABLE_HEYGEN=true`

## Próximos Pasos

- [x] Implementar TTS real (Kokoro)
- [x] Implementar Lip-Sync real (MuseTalk)
- [x] Integrar ElevenLabs como fallback
- [x] Integrar HeyGen como fallback completo
- [ ] Añadir página de estado del video
- [ ] Configurar dominio personalizado
- [ ] Añadir analytics

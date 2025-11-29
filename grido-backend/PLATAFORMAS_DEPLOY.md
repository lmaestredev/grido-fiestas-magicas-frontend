# Análisis de Plataformas de Deploy para Grido

## Requisitos del Sistema

### Frontend (Next.js)
- Hosting estático/serverless
- API Routes
- Variables de entorno
- **Costo esperado:** Bajo (puede ser gratis)

### Worker (Python + GPU)
- GPU para MuseTalk (lip-sync)
- FFmpeg instalado
- Python 3.11+
- Acceso a Redis
- **Costo esperado:** Medio-Alto (GPU es caro)

### Storage
- Almacenamiento de videos (S3-compatible)
- **Costo esperado:** Bajo ($0.02-0.05 por GB)

### Queue/Database
- Redis para jobs
- **Costo esperado:** Bajo-Medio

---

## Opción 1: Vercel + Modal (RECOMENDADA) ⭐

### Arquitectura
```
Vercel (Frontend + API Routes)
    ↓
Modal (Worker con GPU)
    ↓
Cloudflare R2 (Storage)
    ↓
Upstash Redis (Queue)
```

### Vercel (Frontend)
- **Qué es:** Plataforma serverless para Next.js
- **Costo:** 
  - Hobby: GRATIS (100GB bandwidth, 6000 min build)
  - Pro: $20/mes (1TB bandwidth)
- **Pros:**
  - Deploy automático desde GitHub
  - Optimizado para Next.js
  - API Routes incluidas
  - SSL gratis
- **Contras:**
  - Límite de ejecución 10s en Hobby, 60s en Pro
  - No puede correr workers pesados

### Modal (Worker GPU)
- **Qué es:** Plataforma serverless para Python con GPU
- **Costo:** 
  - Pay-as-you-go
  - GPU T4: ~$0.60/hora (~$0.001 por video de 6 segundos)
  - GPU A10G: ~$1.10/hora (más rápido)
  - **Estimado:** $0.001-0.002 por video
- **Pros:**
  - GPU on-demand (solo pagas cuando procesa)
  - Auto-scaling
  - Python nativo
  - FFmpeg pre-instalado
  - Deploy con `modal deploy`
- **Contras:**
  - Requiere cuenta y tarjeta de crédito
  - Cold start inicial (~10-30s primera vez)

### Cloudflare R2 (Storage)
- **Qué es:** Object storage compatible con S3
- **Costo:**
  - Storage: $0.015/GB/mes
  - Egress: GRATIS (vs S3 que cobra)
  - **Estimado:** ~$1-5/mes para miles de videos
- **Pros:**
  - Egress gratis (ahorro enorme vs S3)
  - Compatible con S3 API
  - CDN integrado
- **Contras:**
  - Requiere cuenta Cloudflare

### Upstash Redis (Queue)
- **Qué es:** Redis serverless
- **Costo:**
  - Free: 10,000 comandos/día
  - Pay-as-you-go: $0.20 por 100k comandos
  - **Estimado:** GRATIS o <$5/mes
- **Pros:**
  - Serverless (no servidor que mantener)
  - REST API (funciona desde Vercel)
  - Free tier generoso
- **Contras:**
  - Límites en free tier

### Resend (Email)
- **Qué es:** Servicio de email transaccional
- **Costo:**
  - Free: 100 emails/día
  - Pro: $20/mes (50,000 emails)
  - **Estimado:** GRATIS o $20/mes
- **Pros:**
  - API simple
  - Free tier generoso
  - Buena deliverability

### TOTAL ESTIMADO (Opción 1)
- **Setup inicial:** $0
- **Mensual (bajo volumen):** $0-10/mes
- **Por video:** $0.001-0.002
- **1000 videos/mes:** ~$2-5/mes
- **10,000 videos/mes:** ~$20-50/mes

---

## Opción 2: Railway (Todo en Uno)

### Arquitectura
```
Railway (Frontend + Worker + Redis)
    ↓
Cloudflare R2 (Storage)
```

### Railway
- **Qué es:** PaaS que corre contenedores
- **Costo:**
  - Hobby: $5/mes (500 horas de ejecución)
  - Pro: $20/mes + uso
  - **GPU:** NO DISPONIBLE directamente
- **Pros:**
  - Todo en una plataforma
  - Deploy desde GitHub
  - Redis incluido
  - Fácil de usar
- **Contras:**
  - **NO tiene GPU** (necesitarías usar Modal o RunPod para worker)
  - Más caro que Vercel para frontend
  - Límites de recursos

### TOTAL ESTIMADO (Opción 2)
- **Mensual:** $25-50/mes (Railway + Modal GPU + R2)
- **Por video:** $0.001-0.002

**Veredicto:** Más caro que Opción 1, sin ventajas claras.

---

## Opción 3: Vercel + RunPod

### RunPod (Worker GPU)
- **Qué es:** GPU cloud más barato
- **Costo:**
  - GPU RTX 3090: ~$0.34/hora
  - GPU A40: ~$0.79/hora
  - Serverless: Pay-per-second
  - **Estimado:** $0.0005-0.001 por video
- **Pros:**
  - MÁS BARATO que Modal
  - GPU potentes
  - Serverless disponible
- **Contras:**
  - Más complejo de configurar
  - Menos documentación
  - Requiere Docker custom

### TOTAL ESTIMADO (Opción 3)
- **Mensual:** $0-5/mes
- **Por video:** $0.0005-0.001
- **10,000 videos/mes:** ~$5-15/mes

**Veredicto:** Más barato pero más complejo. Bueno si tenés experiencia con Docker.

---

## Opción 4: VPS + GPU (Hetzner/OVH)

### Arquitectura
```
Vercel (Frontend)
    ↓
VPS con GPU (Worker)
    ↓
Cloudflare R2 (Storage)
```

### VPS con GPU
- **Hetzner:** No tiene GPU
- **OVH:** GPU desde €100/mes
- **Vast.ai:** GPU desde $0.20/hora (~$150/mes 24/7)

**Veredicto:** Solo viable si procesás 24/7. No escalable. NO RECOMENDADO.

---

## Opción 5: Firebase + Cloud Functions + Cloud Run

### Firebase (Frontend + Storage)
- **Costo:**
  - Hosting: Gratis (10GB storage, 360MB/día transfer)
  - Storage: $0.026/GB
  - Functions: $0.40 por millón de invocaciones
- **Pros:**
  - Todo Google
  - Fácil integración
- **Contras:**
  - Cloud Functions NO tiene GPU
  - Necesitarías Cloud Run con GPU (caro)

### Cloud Run con GPU
- **Costo:** ~$2-4/hora con GPU
- **Veredicto:** MUY CARO. NO RECOMENDADO.

---

## Comparación Final

| Plataforma | Costo Mensual | Costo/Video | Complejidad | GPU | Recomendado |
|------------|---------------|-------------|-------------|-----|-------------|
| **Vercel + Modal** | $0-10 | $0.001-0.002 | Media | ✅ Serverless | ⭐⭐⭐⭐⭐ |
| Vercel + RunPod | $0-5 | $0.0005-0.001 | Alta | ✅ Serverless | ⭐⭐⭐⭐ |
| Railway + Modal | $25-50 | $0.001-0.002 | Media | ✅ Serverless | ⭐⭐⭐ |
| VPS + GPU | $150+ | $0 | Alta | ✅ Dedicado | ⭐⭐ |
| Firebase + Cloud Run | $100+ | $0.01+ | Media | ✅ Serverless | ⭐ |

---

## Recomendación Final: Vercel + Modal + Cloudflare R2 + Upstash

### Por qué esta combinación:

1. **Vercel (Frontend)**
   - Gratis hasta 100GB bandwidth
   - Deploy automático
   - Perfecto para Next.js

2. **Modal (Worker GPU)**
   - GPU serverless (solo pagas cuando procesa)
   - $0.001-0.002 por video
   - Auto-scaling
   - Fácil de deployar

3. **Cloudflare R2 (Storage)**
   - Egress GRATIS (vs S3)
   - $0.015/GB storage
   - Compatible S3

4. **Upstash Redis (Queue)**
   - Free tier: 10,000 comandos/día
   - Serverless
   - REST API

5. **Resend (Email)**
   - Free: 100 emails/día
   - API simple

### Costos Proyectados

**Escenario 1: Campaña Pequeña (1,000 videos)**
- Vercel: $0 (free tier)
- Modal: $1-2
- R2: $1
- Upstash: $0 (free tier)
- Resend: $0 (free tier)
- **TOTAL: $2-3**

**Escenario 2: Campaña Media (10,000 videos)**
- Vercel: $0-20 (puede necesitar Pro)
- Modal: $10-20
- R2: $5
- Upstash: $0-5
- Resend: $0-20
- **TOTAL: $15-70**

**Escenario 3: Campaña Grande (100,000 videos)**
- Vercel: $20 (Pro)
- Modal: $100-200
- R2: $50
- Upstash: $20
- Resend: $20
- **TOTAL: $210-310**

---

## Alternativa para Testing: Todo Local + Ngrok

Si querés probar primero sin gastar:

1. **Frontend:** Vercel (gratis)
2. **Worker:** Tu computadora con GPU
3. **Queue:** Redis local
4. **Storage:** Sistema de archivos local + Ngrok para compartir
5. **Email:** Mailtrap (testing)

**Costo:** $0

Una vez que funcione, migrar a Modal.

---

## Próximos Pasos

1. Crear cuenta en Vercel (gratis)
2. Crear cuenta en Modal (requiere tarjeta)
3. Crear cuenta en Cloudflare (gratis)
4. Crear cuenta en Upstash (gratis)
5. Crear cuenta en Resend (gratis)
6. Configurar variables de entorno
7. Deploy!

¿Querés que te ayude con el setup de alguna de estas plataformas?

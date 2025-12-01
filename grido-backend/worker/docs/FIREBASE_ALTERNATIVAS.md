# Alternativas a Firebase Storage

Si no puedes crear claves de Service Account debido a políticas de organización, aquí tienes alternativas:

## Opción 1: Vercel Blob (Más Simple)

Vercel Blob es muy fácil de configurar y no requiere credenciales complejas.

### Configuración:

1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Tu proyecto → **Storage** → **Blob**
3. Haz clic en **Create**
4. Copia el token que aparece

### Variables de entorno:

```bash
STORAGE_TYPE=vercel
VERCEL_BLOB_TOKEN=vercel_blob_xxx
```

### Instalar:

```bash
pip install vercel-blob
```

**Ventajas:**
- ✅ Muy fácil de configurar
- ✅ No requiere Service Accounts
- ✅ URLs públicas automáticas
- ✅ Integrado con Vercel (si ya usas Vercel para el frontend)

**Desventajas:**
- ⚠️ Solo disponible si usas Vercel

---

## Opción 2: Railway Storage (Con Volumen Persistente)

Railway permite guardar archivos en volúmenes persistentes y servirlos a través de tu API.

### Configuración:

1. En Railway, crea un volumen persistente
2. Monta el volumen en tu servicio
3. Crea un endpoint en tu API para servir videos

### Variables de entorno:

```bash
STORAGE_TYPE=railway
RAILWAY_STORAGE_PATH=/app/storage
API_BASE_URL=https://tu-api.railway.app
```

**Ventajas:**
- ✅ No requiere credenciales externas
- ✅ Control total sobre los archivos
- ✅ Gratis hasta cierto límite

**Desventajas:**
- ⚠️ Requiere crear endpoint para servir videos
- ⚠️ Menos escalable que Firebase/Vercel

---

## Opción 3: Cloudflare R2 (Similar a S3)

Cloudflare R2 es compatible con S3 y muy económico.

### Configuración:

1. Ve a [Cloudflare Dashboard](https://dash.cloudflare.com)
2. R2 → Create bucket
3. Manage R2 API Tokens → Create API Token
4. Copia las credenciales

### Variables de entorno:

```bash
STORAGE_TYPE=r2
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=tu-bucket
AWS_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com
```

**Ventajas:**
- ✅ Muy económico (egress gratuito)
- ✅ Compatible con S3
- ✅ Fácil de configurar

**Desventajas:**
- ⚠️ Requiere cuenta de Cloudflare

---

## Opción 4: Crear Service Account en Google Cloud Console

Si el problema es que no puedes crear claves en la cuenta predeterminada, crea una nueva:

### Pasos:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Proyecto: `grido-56fa7`
3. **IAM & Admin** → **Service Accounts**
4. **+ CREATE SERVICE ACCOUNT**
5. Nombre: `firebase-storage-uploader`
6. **CREATE AND CONTINUE**
7. Rol: **Storage Admin** o **Firebase Storage Admin**
8. **CONTINUE** → **DONE**
9. Vuelve a la lista, haz clic en la nueva cuenta
10. **KEYS** → **ADD KEY** → **Create new key** → **JSON**
11. Descarga el archivo

Esta nueva cuenta debería permitir crear claves sin problemas.

---

## Recomendación

Para tu caso, recomiendo:

1. **Primero intenta:** Crear nueva Service Account en Google Cloud Console (Opción 4)
2. **Si no funciona:** Usa Vercel Blob (Opción 1) - es la más simple
3. **Alternativa:** Cloudflare R2 (Opción 3) - muy económico

¿Cuál prefieres probar primero?


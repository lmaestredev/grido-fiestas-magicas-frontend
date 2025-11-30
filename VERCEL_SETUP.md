# Configuración de Vercel para Grido Fiestas Mágicas

## Estructura del Repositorio

```
grido-fiestas-magicas/
├── grido_front/          ← Frontend (Next.js) - ESTO VA A VERCEL
└── grido-backend/        ← Backend (Python/Worker) - NO VA A VERCEL
```

## Configuración en Vercel

### Opción 1: Configuración desde el Dashboard (Recomendado)

1. **Ir a Vercel Dashboard**
   - https://vercel.com/dashboard
   - Click en "Add New..." → "Project"

2. **Importar Repositorio**
   - Selecciona tu repositorio de GitHub: `grido-fiestas-magicas`
   - Click en "Import"

3. **Configurar el Proyecto**
   
   **IMPORTANTE:** Configura estos valores:
   
   - **Framework Preset:** Next.js (debería detectarse automáticamente)
   - **Root Directory:** `grido_front` ⚠️ **ESTO ES CRÍTICO**
   - **Build Command:** `pnpm build` (o `npm run build` si usas npm)
   - **Output Directory:** `.next` (default de Next.js)
   - **Install Command:** `pnpm install` (o `npm install`)

4. **Variables de Entorno**
   
   Agrega estas variables en la sección "Environment Variables":
   
   ```
   UPSTASH_REDIS_REST_URL=https://tu-redis.upstash.io
   UPSTASH_REDIS_REST_TOKEN=tu-token
   VIDEO_API_SECRET=tu-secreto-seguro
   ```

5. **Deploy**
   - Click en "Deploy"
   - Vercel construirá el proyecto desde `grido_front/`

---

### Opción 2: Configuración con vercel.json (Alternativa)

Si prefieres tener la configuración en el código, crea un archivo `vercel.json` en la raíz del repositorio:

```json
{
  "buildCommand": "cd grido_front && pnpm build",
  "outputDirectory": "grido_front/.next",
  "installCommand": "cd grido_front && pnpm install",
  "framework": "nextjs",
  "rootDirectory": "grido_front"
}
```

**Nota:** Con este archivo, Vercel debería detectar automáticamente la configuración.

---

### Opción 3: Usar vercel.json dentro de grido_front

Alternativamente, puedes crear `grido_front/vercel.json`:

```json
{
  "buildCommand": "pnpm build",
  "outputDirectory": ".next",
  "installCommand": "pnpm install"
}
```

Y en el dashboard de Vercel, solo configurar:
- **Root Directory:** `grido_front`

---

## Verificación Post-Deploy

Una vez deployado, verifica:

1. **URL del proyecto:** Deberías ver tu landing en `https://tu-proyecto.vercel.app`

2. **API Route:** Prueba que funcione:
   ```bash
   curl -X POST https://tu-proyecto.vercel.app/api/generate-video \
     -H "Authorization: Bearer tu-secreto" \
     -H "Content-Type: application/json" \
     -d '{"nombre":"Test","email":"test@test.com","provincia":"Buenos Aires","queHizo":"Test","recuerdoEspecial":"Test","pedidoNocheMagica":"Test","parentesco":"Test"}'
   ```

3. **Logs:** Revisa los logs en Vercel Dashboard → Deployments → [tu deploy] → Functions

---

## Estructura de Deploy

```
Vercel detecta:
├── grido_front/          ← Root Directory configurado
│   ├── package.json      ← Vercel lee esto
│   ├── next.config.ts    ← Configuración de Next.js
│   ├── src/              ← Código fuente
│   └── public/           ← Assets estáticos
│
└── grido-backend/        ← IGNORADO por Vercel
    └── worker/           ← Se deploya por separado en Modal
```

---

## Troubleshooting

### Error: "Cannot find module" o "package.json not found"

**Solución:** Verifica que el **Root Directory** esté configurado como `grido_front`

### Error: Build fails

**Solución:** 
1. Verifica que `pnpm-lock.yaml` esté en `grido_front/`
2. Revisa los logs de build en Vercel
3. Asegúrate de que todas las dependencias estén en `package.json`

### Variables de entorno no funcionan

**Solución:**
1. Verifica que estén configuradas en Vercel Dashboard
2. Asegúrate de hacer "Redeploy" después de agregar variables
3. Verifica que los nombres coincidan exactamente (case-sensitive)

### El deploy funciona pero la página está en blanco

**Solución:**
1. Revisa la consola del navegador para errores
2. Verifica que las rutas de imágenes sean correctas (`/images/...`)
3. Revisa los logs de runtime en Vercel

---

## Comandos Útiles

### Deploy manual desde CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Desde la raíz del proyecto
cd grido_front
vercel

# O especificando el directorio
vercel --cwd grido_front
```

### Verificar configuración

```bash
# Ver configuración actual
vercel inspect

# Ver variables de entorno
vercel env ls
```

---

## Notas Importantes

1. **Backend separado:** El directorio `grido-backend/` NO se deploya en Vercel. Solo el frontend (`grido_front/`)

2. **API Routes:** Las API routes de Next.js en `grido_front/src/app/api/` SÍ funcionan en Vercel como Serverless Functions

3. **Variables de entorno:** Solo necesitas las variables del frontend en Vercel. Las del backend van en Modal

4. **Build time:** El build solo procesa `grido_front/`, no todo el repositorio

---

## Checklist de Configuración

- [ ] Repositorio conectado a Vercel
- [ ] Root Directory configurado como `grido_front`
- [ ] Framework detectado como Next.js
- [ ] Build Command: `pnpm build` (o `npm run build`)
- [ ] Variables de entorno configuradas:
  - [ ] `UPSTASH_REDIS_REST_URL`
  - [ ] `UPSTASH_REDIS_REST_TOKEN`
  - [ ] `VIDEO_API_SECRET`
- [ ] Primer deploy exitoso
- [ ] Landing page visible en la URL de Vercel
- [ ] API route `/api/generate-video` funcionando

---

## URLs de Referencia

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Documentación Vercel:** https://vercel.com/docs
- **Monorepos en Vercel:** https://vercel.com/docs/monorepos


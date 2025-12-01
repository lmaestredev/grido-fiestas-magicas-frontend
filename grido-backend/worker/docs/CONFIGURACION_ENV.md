# Configuración de Variables de Entorno (.env)

## Credenciales de APIs

### ✅ Sync Labs (Ya configurado)
```bash
SYNCLABS_API_KEY=tu_api_key_aqui
```
**Ubicación en .env**: Líneas 26-27

---

### ✅ ElevenLabs (Actualizado)
```bash
ELEVENLABS_API_KEY=tu_api_key_aqui
PAPA_NOEL_VOICE_ID=bkVwoLpm00fYfz45ZQAb
```

**Nota**: La voice ID de Papá Noel ha sido actualizada a `bkVwoLpm00fYfz45ZQAb`

---

### ✅ Higgsfield (Nuevo)
```bash
HIGGSFIELD_API_KEY_ID=a242bf13-bfe5-4aa4-af63-245d05d48d22
HIGGSFIELD_API_KEY_SECRET=19b359462d24010924f52a74048d9ab190f2d0336f48a758bd0f1ccc242b4b1a
```

**Credenciales proporcionadas:**
- API Key ID: `a242bf13-bfe5-4aa4-af63-245d05d48d22`
- API Key Secret: `19b359462d24010924f52a74048d9ab190f2d0336f48a758bd0f1ccc242b4b1a`

---

## Ejemplo Completo de .env

```bash
# TTS Providers
ELEVENLABS_API_KEY=tu_elevenlabs_key
PAPA_NOEL_VOICE_ID=bkVwoLpm00fYfz45ZQAb

# Lip-Sync Providers
SYNCLABS_API_KEY=tu_synclabs_key

# Video Providers
HEYGEN_API_KEY=tu_heygen_key
PAPA_NOEL_AVATAR_ID=default

# Higgsfield (nuevo)
HIGGSFIELD_API_KEY_ID=a242bf13-bfe5-4aa4-af63-245d05d48d22
HIGGSFIELD_API_KEY_SECRET=19b359462d24010924f52a74048d9ab190f2d0336f48a758bd0f1ccc242b4b1a

# Storage
STORAGE_TYPE=local

# Redis
REDIS_URL=redis://localhost:6379

# Email
RESEND_API_KEY=tu_resend_key
```

---

## Verificación

Para verificar que las credenciales están cargadas correctamente:

```bash
cd grido-backend/worker
source venv/bin/activate
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('✅ Sync Labs:', 'Configurado' if os.getenv('SYNCLABS_API_KEY') else '❌ No configurado')
print('✅ ElevenLabs:', 'Configurado' if os.getenv('ELEVENLABS_API_KEY') else '❌ No configurado')
print('✅ Voice ID:', os.getenv('PAPA_NOEL_VOICE_ID', 'No configurado'))
print('✅ Higgsfield ID:', 'Configurado' if os.getenv('HIGGSFIELD_API_KEY_ID') else '❌ No configurado')
print('✅ Higgsfield Secret:', 'Configurado' if os.getenv('HIGGSFIELD_API_KEY_SECRET') else '❌ No configurado')
"
```


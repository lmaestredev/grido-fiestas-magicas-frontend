# Solución para HeyGen API

## Problema Actual

HeyGen está devolviendo 404 en todos los endpoints probados:
- `https://api.heygen.com/v2/video.generate` ❌
- `https://api.heygen.com/v2/video/talking_photo` ❌
- `https://api.heygen.com/v1/video.generate` ❌
- `https://api.heygen.com/v1/talking_photo` ❌

## Soluciones

### Opción 1: Usar ElevenLabs (Recomendado para pruebas)

ElevenLabs es más directo para TTS y funciona bien:

1. Obtener API key de ElevenLabs:
   - Ve a https://elevenlabs.io
   - Crea cuenta o inicia sesión
   - Ve a Profile → API Key
   - Copia la API key

2. Configurar en `.env`:
   ```bash
   ELEVENLABS_API_KEY=tu_api_key_aqui
   PAPA_NOEL_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # O busca una voz masculina
   ```

3. Probar:
   ```bash
   python3 test_audio_generation.py
   ```

### Opción 2: Buscar Documentación Correcta de HeyGen

1. Ve a https://docs.heygen.com
2. Busca el endpoint correcto para generar videos
3. Actualiza `providers/heygen_video.py` con el endpoint correcto

### Opción 3: Usar HeyGen SDK (si existe)

HeyGen puede tener un SDK oficial de Python que maneje los endpoints correctamente.

---

## Estado Actual

- ✅ HeyGen API key configurada
- ✅ Avatares disponibles (verificados)
- ❌ Endpoint de generación de video no funciona (404)

## Próximos Pasos

1. **Para pruebas inmediatas:** Usar ElevenLabs
2. **Para producción:** Buscar/corregir endpoint de HeyGen o usar SDK oficial


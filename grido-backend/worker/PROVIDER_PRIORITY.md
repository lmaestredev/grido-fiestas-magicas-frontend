# Orden de Prioridad de Providers

Este documento define el orden de prioridad de los providers para generar videos con la mejor calidad y máxima resiliencia.

## 🎯 Estrategia de Fallback

El sistema intenta usar los providers en este orden, cayendo al siguiente si el anterior falla:

### Video Providers (Solución Completa - TTS + Lip-sync)

**Orden de Prioridad:**
1. **HeyGen** ⭐ PRIORIDAD 1
   - Mejor calidad y sincronización
   - API completa con TTS + lip-sync integrado
   - Requiere: `HEYGEN_API_KEY`
   
2. **Higgsfield** ⭐ PRIORIDAD 2
   - Alternativa de alta calidad
   - API completa con TTS + lip-sync integrado
   - Requiere: `HIGGSFIELD_API_KEY_ID` y `HIGGSFIELD_API_KEY_SECRET`

### Lip-sync Providers (Solo sincronización de labios)

**Orden de Prioridad:**
1. **Wav2Lip** ⭐ PRIORIDAD 1
   - Open-source, confiable
   - Requiere: Instalación local de Wav2Lip
   
2. **Sync Labs** ⭐ PRIORIDAD 2
   - Comercial HD, alta calidad
   - Requiere: `SYNCLABS_API_KEY`

### TTS Providers (Solo Text-to-Speech)

**Orden de Prioridad:**
1. **ElevenLabs** ⭐ ÚNICO
   - Alta calidad de voz
   - Requiere: `ELEVENLABS_API_KEY`
   - Usado en Strategy 2 y 3 (cuando no hay video providers)

## 🔄 Flujo de Estrategias

```
┌─────────────────────────────────────────────────────────┐
│ Strategy 1: Video Providers (PRIORIDAD MÁXIMA)          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 1. HeyGen → 2. Higgsfield                           │ │
│ │ Genera video completo con TTS + lip-sync integrado  │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                    ↓ (si falla)
┌─────────────────────────────────────────────────────────┐
│ Strategy 2: TTS + Lip-sync                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ TTS: ElevenLabs                                     │ │
│ │ Lip-sync: 1. Wav2Lip → 2. Sync Labs                 │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                    ↓ (si falla)
┌─────────────────────────────────────────────────────────┐
│ Strategy 3: TTS + Base Video (FALLBACK FINAL)           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ TTS: ElevenLabs                                     │ │
│ │ Video: Base video sin lip-sync (solo audio)        │ │
│ │ ⚠️  Sin sincronización de labios                   │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 📋 Configuración Recomendada

### Para Máxima Calidad (Recomendado)
```bash
# Video Providers (completos)
HEYGEN_API_KEY=tu_key              # PRIORIDAD 1
HIGGSFIELD_API_KEY_ID=tu_id        # PRIORIDAD 2
HIGGSFIELD_API_KEY_SECRET=tu_secret

# TTS (para Strategy 2 y 3)
ELEVENLABS_API_KEY=tu_key
PAPA_NOEL_VOICE_ID=tu_voice_id

# Lip-sync (para Strategy 2)
WAV2LIP_REPO_PATH=/path/to/Wav2Lip    # PRIORIDAD 1
# O
SYNCLABS_API_KEY=tu_key              # PRIORIDAD 2
```

### Para Desarrollo/Pruebas
```bash
# Mínimo necesario
ELEVENLABS_API_KEY=tu_key
PAPA_NOEL_VOICE_ID=tu_voice_id

# Opcional (mejora calidad)
HEYGEN_API_KEY=tu_key
```

## 🎯 Objetivo

**Generar la mayor cantidad de videos con la misma calidad** usando:
1. HeyGen como primera opción (mejor calidad)
2. Higgsfield como segunda opción (alta calidad)
3. Wav2Lip como tercera opción (buena calidad)
4. ElevenLabs + base video como última opción (funcional pero sin lip-sync)

## 📊 Métricas de Éxito

- **Tasa de éxito Strategy 1 (Video Providers)**: > 80%
- **Tasa de éxito Strategy 2 (TTS + Lip-sync)**: > 15%
- **Tasa de éxito Strategy 3 (Fallback)**: < 5%

## 🔧 Deshabilitar Providers

Si quieres deshabilitar un provider específico:

```bash
# En .env
DISABLE_HEYGEN=true
DISABLE_HIGGSFIELD=true
DISABLE_WAV2LIP=true
DISABLE_SYNCLABS=true
DISABLE_ELEVENLABS=true
```

## 📝 Notas

- El sistema siempre intenta usar el provider de mayor prioridad primero
- Si un provider falla, automáticamente intenta el siguiente
- Strategy 3 (fallback final) siempre funciona si hay TTS disponible
- Los video providers (HeyGen, Higgsfield) generan mejor calidad que TTS + lip-sync separado


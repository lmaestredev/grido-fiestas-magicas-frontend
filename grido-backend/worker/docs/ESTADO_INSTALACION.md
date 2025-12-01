# Estado de Instalación - MuseTalk y Wav2Lip

## ✅ Completado

### 1. Repositorios Clonados
- ✅ **MuseTalk**: Clonado en `grido-backend/worker/MuseTalk`
- ✅ **Wav2Lip**: Clonado en `grido-backend/worker/wav2lip`

### 2. Scripts Encontrados
- ✅ **Wav2Lip**: `wav2lip/inference.py` existe
- ⚠️ **MuseTalk**: No tiene `realtime_inference.py`, tiene `app.py`, `train.py`

### 3. Variables de Entorno Configuradas
Agregadas al `.env`:
```bash
# MuseTalk
MUSETALK_MODEL_PATH=
MUSETALK_SCRIPT_PATH=MuseTalk/realtime_inference.py

# Wav2Lip
WAV2LIP_REPO_PATH=/path/to/wav2lip
WAV2LIP_MODEL_PATH=/path/to/wav2lip/checkpoints/wav2lip_gan.pth
```

### 4. ProviderManager Actualizado
- ✅ Wav2Lip detectado como disponible
- ⚠️ MuseTalk necesita ajustes (script correcto)

## ⚠️ Pendiente

### 1. Dependencias de Wav2Lip
**Problema**: Las dependencias requieren versiones muy antiguas:
- torch==1.1.0 (muy antiguo)
- numpy==1.17.1 (muy antiguo)
- opencv-python==4.1.0.25

**Solución**: 
- Opción A: Instalar en un entorno virtual separado
- Opción B: Usar versiones más nuevas y ajustar el código si es necesario
- Opción C: Usar solo MuseTalk (más moderno)

### 2. Dependencias de MuseTalk
**Problema**: Algunas dependencias pueden tener conflictos

**Solución**: Instalar cuidadosamente o usar un entorno separado

### 3. Modelos Requeridos
- ⚠️ **Wav2Lip**: Necesita `wav2lip_gan.pth` (ver `DESCARGAR_MODELOS.md`)
- ⚠️ **MuseTalk**: Descarga modelos automáticamente, pero puede requerir configuración

### 4. Script de MuseTalk
**Problema**: No existe `realtime_inference.py`

**Solución**: 
- Actualizar provider para usar `app.py` o el script correcto
- O verificar la documentación de MuseTalk para el script correcto

## Recomendaciones

### Opción 1: Usar Solo Wav2Lip (Más Simple)
1. Descargar modelo `wav2lip_gan.pth`
2. Instalar dependencias básicas (puede requerir entorno separado)
3. Configurar variables de entorno

### Opción 2: Usar Solo MuseTalk (Más Moderno)
1. Verificar documentación de MuseTalk para uso correcto
2. Instalar dependencias
3. Ajustar provider para usar el script correcto

### Opción 3: Usar Ambos (Máxima Compatibilidad)
1. Instalar en entornos virtuales separados
2. Configurar ambos providers
3. El sistema usará el que esté disponible

## Próximos Pasos Inmediatos

1. **Descargar modelo de Wav2Lip**:
   ```bash
   cd grido-backend/worker/wav2lip
   mkdir -p checkpoints
   # Descargar wav2lip_gan.pth (ver DESCARGAR_MODELOS.md)
   ```

2. **Verificar script de MuseTalk**:
   - Revisar README.md de MuseTalk
   - Identificar el script correcto para inferencia
   - Actualizar provider si es necesario

3. **Probar providers**:
   ```bash
   python3 -c "from providers.manager import ProviderManager; m = ProviderManager(); print(m.lipsync_providers)"
   ```

## Estado Actual del Sistema

- ✅ **Wav2Lip**: Detectado pero necesita modelo
- ⚠️ **MuseTalk**: Necesita ajuste de script
- ✅ **Strategy 3**: Funcionando (TTS + Base Video sin lip-sync)

El sistema puede funcionar ahora mismo con Strategy 3, y cuando se configuren los modelos, usará lip-sync automáticamente.


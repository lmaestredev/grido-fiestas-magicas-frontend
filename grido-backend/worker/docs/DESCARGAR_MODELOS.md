# Descargar Modelos para Lip-Sync

## Wav2Lip - Modelos Requeridos

### 1. Modelo Principal: wav2lip_gan.pth

**Descargar desde:**
- Repositorio oficial: https://github.com/Rudrabha/Wav2Lip#pre-trained-models
- Link directo de Google Drive: https://drive.google.com/file/d/15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk/view?usp=share_link
- Carpeta completa: https://drive.google.com/drive/folders/153HLrqlBNxzZcHi17PEvP09kkAfzRshM?usp=share_link

**⚠️ IMPORTANTE**: Google Drive requiere autenticación para archivos grandes. Opciones:

**Opción A: Descarga Manual (Recomendada)**
1. Abre el link en tu navegador: https://drive.google.com/file/d/15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk/view?usp=share_link
2. Descarga el archivo `wav2lip_gan.pth`
3. Colócalo en: `grido-backend/worker/wav2lip/checkpoints/wav2lip_gan.pth`

**Opción B: Con gdown (requiere autenticación de Google)**
```bash
cd grido-backend/worker/wav2lip/checkpoints
pip install gdown
gdown "https://drive.google.com/uc?id=15G3U08c8xsCkOqQxE38Z2XXDnPcOptNk" -O wav2lip_gan.pth
```

**Ubicación:**
```bash
cd grido-backend/worker/wav2lip
mkdir -p checkpoints
# Mover el archivo descargado a: checkpoints/wav2lip_gan.pth
```

**Tamaño esperado**: ~350 MB

### 2. Modelo de Detección de Rostros: s3fd.pth ✅ DESCARGADO

**✅ Ya descargado**: `face_detection/detection/sfd/s3fd.pth` (86 MB)

**Link alternativo** (si necesitas re-descargar):
- https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth

## MuseTalk - Modelos Requeridos

MuseTalk descarga los modelos automáticamente la primera vez que se usa desde HuggingFace.

### Modelos Principales

**Descargar desde:**
- Repositorio oficial: https://github.com/TMElyralab/MuseTalk#model-checkpoints
- HuggingFace: https://huggingface.co/TMElyralab/MuseTalk

**Ubicación típica:**
```bash
cd grido-backend/worker/MuseTalk
mkdir -p checkpoints
# Los modelos se descargan automáticamente la primera vez
```

## Sync Labs API (Versión Comercial de Wav2Lip) ✅ CONFIGURADO

**✅ API Key configurada** en `.env`:
```bash
SYNCLABS_API_KEY=sk--TYpSgoITA-NougeRyXsmw.wPoj709byT7yLe16FiZiJLgxadbHW3yi
```

**Documentación**: https://synclabs.so/

**Ventajas**:
- Modelos HD (192x288)
- Mejor calidad que Wav2Lip open-source
- Soporte comercial
- No requiere descargar modelos localmente

**Nota**: Sync Labs es la versión comercial y mejorada de Wav2Lip. El provider está implementado y configurado.

## Orden de Preferencia de Providers

El sistema intentará usar los providers en este orden:

1. **MuseTalk** (local, open-source) - Más rápido
2. **Sync Labs** (API comercial) - Mejor calidad HD ✅ CONFIGURADO
3. **Wav2Lip** (local, open-source) - Requiere modelo descargado

## Verificación

Después de descargar los modelos, verifica que existan:

```bash
# Wav2Lip
ls -lh grido-backend/worker/wav2lip/checkpoints/wav2lip_gan.pth
# Debe ser ~350 MB, NO 2.4K (ese es un error HTML)

ls -lh grido-backend/worker/wav2lip/face_detection/detection/sfd/s3fd.pth
# Debe ser ~86 MB ✅

# MuseTalk (si descargaste manualmente)
ls -lh grido-backend/worker/MuseTalk/checkpoints/
```

## Estado Actual

- ✅ **Sync Labs**: Configurado y disponible (no requiere modelos)
- ✅ **MuseTalk**: Disponible (descarga modelos automáticamente)
- ✅ **s3fd.pth**: Descargado (86 MB)
- ⚠️ **wav2lip_gan.pth**: Requiere descarga manual desde Google Drive

## Troubleshooting

### Error: wav2lip_gan.pth es muy pequeño (2.4K)

Esto significa que se descargó un HTML de error en lugar del modelo. Solución:
1. Descarga manualmente desde el navegador
2. O usa gdown con autenticación de Google

### Error al descargar desde Google Drive

Google Drive requiere autenticación para archivos grandes:
1. **Mejor opción**: Descarga manual desde el navegador
2. O autentica gdown: `gdown --fuzzy "URL"`

### Verificar integridad del modelo

```bash
# Wav2Lip
file checkpoints/wav2lip_gan.pth
# Debe mostrar: "data" o similar, NO "HTML document"
```

## Notas Importantes

- **Sync Labs ya está configurado** y no requiere descargar modelos ✅
- **MuseTalk descarga automáticamente** los modelos la primera vez
- **Wav2Lip open-source** requiere descarga manual del modelo (opcional si usas Sync Labs)

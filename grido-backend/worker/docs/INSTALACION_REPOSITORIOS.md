# Instalación de Repositorios - MuseTalk y Wav2Lip

## Instalación Manual Requerida

Los repositorios de MuseTalk y Wav2Lip **NO** están incluidos en el repositorio principal (están en `.gitignore`). Debes clonarlos manualmente.

## Pasos de Instalación

### 1. MuseTalk

```bash
cd grido-backend/worker
git clone https://github.com/TMElyralab/MuseTalk.git
```

### 2. Wav2Lip

```bash
cd grido-backend/worker
git clone https://github.com/Rudrabha/Wav2Lip.git wav2lip
```

### 3. Instalar Dependencias

#### MuseTalk
```bash
cd grido-backend/worker/MuseTalk
source ../venv/bin/activate
pip install -r requirements.txt
```

#### Wav2Lip
```bash
cd grido-backend/worker/wav2lip
source ../venv/bin/activate
pip install -r requirements.txt
```

**Nota**: Wav2Lip requiere versiones muy antiguas que pueden causar conflictos. Considera usar un entorno virtual separado.

### 4. Descargar Modelos

Ver `DESCARGAR_MODELOS.md` para instrucciones detalladas.

#### Wav2Lip (Requerido)
- Descargar `wav2lip_gan.pth` y colocarlo en `wav2lip/checkpoints/`

#### MuseTalk
- Descarga modelos automáticamente la primera vez que se usa

## Verificación

Después de instalar, verifica que los providers estén disponibles:

```bash
cd grido-backend/worker
source venv/bin/activate
python3 -c "from providers.manager import ProviderManager; m = ProviderManager(); print(f'Lip-sync providers: {len(m.lipsync_providers)}')"
```

Deberías ver:
- `Lip-sync providers: 2` (MuseTalk y Wav2Lip)

## Notas

- Los repositorios están en `.gitignore` para evitar conflictos
- Cada desarrollador debe clonarlos manualmente
- Los modelos deben descargarse por separado
- Las dependencias pueden requerir entornos virtuales separados


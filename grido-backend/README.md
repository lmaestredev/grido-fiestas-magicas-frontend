# Grido Backend - Video Generation Worker

Sistema de generación de videos personalizados de Papá Noel para Grido Fiestas Mágicas. El worker procesa solicitudes de forma asíncrona desde una cola Redis, genera videos usando múltiples proveedores de IA y los compone en un video final.

## Descripción

Este backend procesa solicitudes de generación de videos personalizados que incluyen:
- Generación de audio con TTS (Text-to-Speech)
- Aplicación de lip-sync a videos base
- Composición de videos finales combinando intro, video principal y outro
- Subida de videos generados a storage (Firebase, S3, Vercel Blob, etc.)

## Requisitos

- Python 3.8+
- Redis (para la cola de trabajos)
- FFmpeg (para procesamiento de video)
- Variables de entorno configuradas (ver `.env.example`)

## Instalación

```bash
cd worker
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuración

1. Copia `firebase-credentials.json.example` a `firebase-credentials.json` y configura tus credenciales
2. Crea un archivo `.env` en la carpeta `worker/` con las variables necesarias:
   - `REDIS_URL`: URL de conexión a Redis
   - `HEYGEN_API_KEY`: API key de HeyGen (opcional)
   - `DID_API_KEY`: API key de D-ID (opcional)
   - `ELEVENLABS_API_KEY`: API key de ElevenLabs (opcional)
   - Variables de storage según el proveedor elegido

## Ejecución

### Worker local

```bash
cd worker
python video-worker.py
```

El worker se conectará a Redis y comenzará a procesar trabajos de la cola `video:queue`.

### Verificar configuración

```bash
cd worker
python verificar_config.py
```

Este script valida que al menos un proveedor de IA esté configurado correctamente.

### Health check

```bash
cd worker
python health_check.py
```

Verifica el estado de los servicios y proveedores configurados.

## Estructura del Proyecto

- `worker/`: Código principal del worker
  - `providers/`: Proveedores de IA (HeyGen, D-ID, ElevenLabs, etc.)
  - `config/`: Configuración de proveedores
  - `utils/`: Utilidades (cache, logging, retry, etc.)
  - `tests/`: Tests unitarios
  - `assets/`: Videos y recursos base

## Proveedores Soportados

- **HeyGen**: Generación completa de video con TTS y lip-sync
- **D-ID**: Generación de video con imagen y audio
- **Higgsfield**: Generación de video con IA
- **ElevenLabs**: Text-to-Speech
- **Wav2Lip**: Lip-sync local

El sistema selecciona automáticamente el primer proveedor disponible según el orden de prioridad configurado.


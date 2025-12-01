# ✅ Configuración de Firebase Completada

## Estado Actual

✅ **Archivo de credenciales:** `grido-backend/worker/firebase-credentials.json`
✅ **Project ID:** `grido-479823`
✅ **Service Account:** `firebase-storage-uploader@grido-479823.iam.gserviceaccount.com`
✅ **Storage Bucket:** `grido-479823.firebasestorage.app`

## Próximos Pasos

### 1. Crear archivo `.env` en `grido-backend/worker/`

Crea un archivo `.env` con esta configuración:

```bash
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### 2. Verificar que Firebase Storage esté habilitado

1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Selecciona el proyecto `grido-479823`
3. Ve a **Storage** en el menú lateral
4. Si no está habilitado, haz clic en **Get Started**
5. Configura las reglas de seguridad (ver abajo)

### 3. Configurar Reglas de Storage

Ve a **Storage** → **Rules** y pega esto:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Permitir lectura pública de videos
    match /videos/{videoId} {
      allow read: if true;
      allow write: if false; // Solo desde el backend con credenciales de servicio
    }
  }
}
```

Haz clic en **Publish**.

### 4. Instalar Dependencias

```bash
cd grido-backend/worker
pip install firebase-admin
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

### 5. Probar la Configuración

```bash
cd grido-backend/worker
python test_local.py
```

El script debería:
1. ✅ Generar un video de prueba
2. ✅ Subirlo a Firebase Storage
3. ✅ Mostrar la URL pública del video

## Verificar que Funciona

1. **Ejecuta prueba local:**
   ```bash
   cd grido-backend/worker
   python test_local.py
   ```

2. **Verifica en Firebase Console:**
   - Ve a Storage → Files
   - Deberías ver una carpeta `videos/` con el video de prueba

3. **Prueba la URL pública:**
   - Copia la URL que muestra el script
   - Ábrela en el navegador
   - Deberías poder ver/reproducir el video

## Seguridad

✅ El archivo `firebase-credentials.json` está en `.gitignore` y **NO se subirá a Git**.

⚠️ **NUNCA** subas el archivo de credenciales a un repositorio público.

## URLs Generadas

Las URLs generadas tendrán este formato:
```
https://firebasestorage.googleapis.com/v0/b/grido-479823.firebasestorage.app/o/videos%2F{video_id}.mp4?alt=media&token={token}
```

Estas URLs son públicas y pueden ser compartidas directamente.

## Configuración en Modal (Producción)

Cuando estés listo para producción, agrega estas variables al secreto `grido-secrets` en Modal:

```bash
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"grido-479823",...}'
```

**Nota:** Para `FIREBASE_CREDENTIALS_JSON`, abre el archivo `firebase-credentials.json`, copia todo el contenido y conviértelo a una sola línea (sin saltos de línea).


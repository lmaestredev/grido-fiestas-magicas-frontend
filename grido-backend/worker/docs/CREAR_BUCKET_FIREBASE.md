# Crear Bucket de Firebase Storage

El error indica que el bucket `grido-479823.firebasestorage.app` no existe. Sigue estos pasos para crearlo:

## Pasos para Crear el Bucket

1. **Ve a Firebase Console:**
   - Abre [Firebase Console](https://console.firebase.google.com)
   - Selecciona el proyecto `grido-479823`

2. **Habilita Firebase Storage:**
   - En el menú lateral, haz clic en **Storage**
   - Si ves "Get Started", haz clic ahí
   - Si ya está habilitado pero no hay buckets, ve al paso siguiente

3. **Crear Bucket (si es necesario):**
   - Ve a [Google Cloud Console](https://console.cloud.google.com)
   - Selecciona el proyecto `grido-479823`
   - Ve a **Cloud Storage** → **Buckets**
   - Haz clic en **CREATE BUCKET**
   - Nombre: `grido-479823.firebasestorage.app` (o el que prefieras)
   - Ubicación: Elige la más cercana (ej: `us-central1`)
   - Storage class: `Standard`
   - Access control: `Uniform`
   - Haz clic en **CREATE**

4. **Verificar en Firebase:**
   - Vuelve a Firebase Console → Storage
   - Deberías ver el bucket listado

## Configurar Reglas de Storage

Una vez creado el bucket, configura las reglas:

1. En Firebase Console → Storage → Rules
2. Pega esto:

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

3. Haz clic en **Publish**

## Probar de Nuevo

Una vez creado el bucket, ejecuta:

```bash
cd grido-backend/worker
source venv/bin/activate
python3 test_storage_only.py
```

## Nota sobre el Nombre del Bucket

El nombre del bucket puede ser diferente. Si creas un bucket con otro nombre, actualiza `.env`:

```bash
FIREBASE_STORAGE_BUCKET=tu-bucket-nombre.appspot.com
```

O si usas el formato estándar de Firebase:
```bash
FIREBASE_STORAGE_BUCKET=grido-479823.appspot.com
```


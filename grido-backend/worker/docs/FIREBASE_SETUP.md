# Configuración de Firebase Storage

Esta guía te ayuda a configurar Firebase Storage para almacenar los videos generados.

## Información del Proyecto

- **Project ID**: `grido-479823`
- **Storage Bucket**: `grido-479823.firebasestorage.app`
- **Auth Domain**: `grido-479823.firebaseapp.com`

## Pasos para Configurar

### 1. Obtener Credenciales de Servicio (Service Account)

Para que el backend en Python pueda subir videos a Firebase Storage, necesitas las credenciales de una Service Account.

#### Opción A: Crear Nueva Service Account (Recomendado si hay restricciones)

Si recibes el error "No se permite crear claves en esta cuenta de servicio", crea una nueva:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona el proyecto `grido-56fa7`
3. Ve a **IAM & Admin** → **Service Accounts**
4. Haz clic en **+ CREATE SERVICE ACCOUNT**
5. Nombre: `firebase-storage-uploader`
6. Descripción: `Service account para subir videos a Firebase Storage`
7. Haz clic en **CREATE AND CONTINUE**
8. En **Grant this service account access to project**:
   - Rol: **Storage Admin** (o **Firebase Storage Admin**)
   - Haz clic en **CONTINUE** → **DONE**
9. Vuelve a la lista de Service Accounts
10. Haz clic en la cuenta que acabas de crear
11. Ve a la pestaña **KEYS**
12. Haz clic en **ADD KEY** → **Create new key**
13. Selecciona **JSON** y haz clic en **CREATE**
14. Se descargará el archivo JSON
15. **Guarda este archivo de forma segura** (no lo subas a Git)

#### Opción B: Usar Service Account Existente

Si ya tienes una Service Account con permisos:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona el proyecto `grido-56fa7`
3. Ve a **IAM & Admin** → **Service Accounts**
4. Selecciona una Service Account existente
5. Ve a la pestaña **KEYS**
6. Si puedes crear una clave, hazlo. Si no, ve a la Opción C.

#### Opción C: Application Default Credentials (Solo en Google Cloud)

Si estás ejecutando en Google Cloud (Cloud Run, Compute Engine, etc.):

1. No necesitas descargar credenciales
2. El código usará automáticamente Application Default Credentials
3. Asegúrate de que la instancia tenga el rol **Storage Admin**

### 2. Alternativa: Usar gcloud CLI (Para desarrollo local)

Si no puedes crear claves, puedes usar Application Default Credentials:

```bash
# Instalar Google Cloud SDK
# macOS:
brew install google-cloud-sdk

# O descarga desde: https://cloud.google.com/sdk/docs/install

# Autenticar
gcloud auth application-default login

# Seleccionar proyecto
gcloud config set project grido-479823
```

Con esto, no necesitas configurar `FIREBASE_CREDENTIALS_PATH` ni `FIREBASE_CREDENTIALS_JSON`. El código detectará automáticamente las credenciales.

**Nota:** Esto solo funciona para desarrollo local. Para producción (Modal), necesitas usar una Service Account con archivo JSON.

### 3. Configurar Variables de Entorno

Tienes dos opciones para configurar las credenciales:

#### Opción A: Archivo de Credenciales (Recomendado para desarrollo local y producción)

Si creaste una nueva Service Account (Opción A del paso 1):

```bash
# En grido-backend/worker/.env
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

**Pasos:**
1. Copia el archivo JSON descargado a `grido-backend/worker/`
2. Agrega el archivo a `.gitignore` para no subirlo por error
3. Configura la ruta en `.env`

#### Opción B: Variable de Entorno JSON (Recomendado para producción/Modal)

Si creaste una nueva Service Account (Opción A del paso 1):

```bash
# En Modal secrets o variables de entorno
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"grido-479823",...}'

**Pasos:**
1. Abre el archivo JSON descargado
2. Copia todo el contenido
3. Conviértelo a una sola línea (sin saltos de línea)
4. Agrega como variable de entorno `FIREBASE_CREDENTIALS_JSON`

#### Opción C: Application Default Credentials (Solo desarrollo local)

Si usaste `gcloud auth application-default login`:

```bash
# No necesitas configurar credenciales, solo:
STORAGE_TYPE=firebase
FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app
```

### 4. Configurar Permisos de Storage

1. Ve a [Firebase Console](https://console.firebase.google.com) → Tu proyecto
2. Ve a **Storage** en el menú lateral
3. Si no tienes un bucket, haz clic en **Get Started**
4. Configura las reglas de seguridad:

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

5. Ve a **Rules** → **Publish**

### 5. Instalar Dependencias

```bash
cd grido-backend/worker
pip install firebase-admin
```

O instala todas las dependencias:

```bash
pip install -r requirements.txt
```

### 6. Probar la Configuración

Ejecuta el script de prueba local:

```bash
python test_local.py
```

El script debería:
1. ✅ Generar un video de prueba
2. ✅ Subirlo a Firebase Storage
3. ✅ Mostrar la URL pública del video

## Configuración en Modal (Producción)

Si estás usando Modal para el worker en producción:

1. **Crear secreto en Modal:**
   ```bash
   modal secret create grido-secrets \
     STORAGE_TYPE=firebase \
     FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app \
     FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
   ```

2. **O desde la UI de Modal:**
   - Ve a [Modal Dashboard](https://modal.com/apps)
   - Secrets → Create Secret
   - Nombre: `grido-secrets`
   - Agrega las variables:
     - `STORAGE_TYPE=firebase`
     - `FIREBASE_STORAGE_BUCKET=grido-479823.firebasestorage.app`
     - `FIREBASE_CREDENTIALS_JSON` (pega el JSON completo en una línea)

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

## Estructura de Archivos en Firebase Storage

```
firebase-storage/
└── videos/
    ├── test_1234567890.mp4
    ├── test_1234567891.mp4
    └── ...
```

## Solución de Problemas

### Error: "FIREBASE_CREDENTIALS_PATH o FIREBASE_CREDENTIALS_JSON requerido"
- Verifica que hayas configurado una de las dos variables
- Asegúrate de que el archivo JSON existe si usas `FIREBASE_CREDENTIALS_PATH`

### Error: "Permission denied"
- Verifica las reglas de Storage en Firebase Console
- Asegúrate de que la Service Account tenga permisos (debería tenerlos por defecto)

### Error: "Bucket not found"
- Verifica que `FIREBASE_STORAGE_BUCKET` sea correcto: `grido-479823.firebasestorage.app`
- Asegúrate de que el bucket existe en Firebase Console

### Error: "firebase-admin no está instalado"
```bash
pip install firebase-admin
```

## URLs Generadas

Las URLs generadas tendrán este formato:
```
https://firebasestorage.googleapis.com/v0/b/grido-479823.firebasestorage.app/o/videos%2F{video_id}.mp4?alt=media&token={token}
```

Estas URLs son públicas y pueden ser compartidas directamente.


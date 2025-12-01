# 📁 Assets Requeridos - Videos Base

## Ubicación
Todos los videos deben estar en: **`grido-backend/worker/assets/`**

---

## Videos Requeridos

### 1. Intro + Frames 1-2-3
- **Nombre:** `Frames_1_2_to_3.mov`
- **Contenido:** Intro del logo de Grido + Pote moviéndose (sin VO de Papá Noel)
- **Formato:** `.mov` (para mantener transparencia)
- **Estado:** ✅ Ya existe

### 2. Frame 3 - Base de Papá Noel (Opcional)
- **Nombre:** `frame3_santa_base.mp4`
- **Contenido:** Papá Noel estático, mirando a cámara, sin hablar
- **Formato:** `.mp4` (puede ser `.mov` también)
- **Duración:** ~15-20 segundos (debe ser más largo que cualquier diálogo posible)
- **Uso:** Solo para Strategy 1 (TTS + Lip-sync)
- **Estado:** ❌ **FALTA** - Necesitas crearlo/exportarlo

### 3. Outro - Cierre
- **Nombre:** `Frame_4_NocheMagica.mov`
- **Contenido:** Cierre de la Noche Mágica
- **Formato:** `.mov` (para mantener transparencia)
- **Estado:** ✅ Ya existe

---

## Especificaciones Técnicas

### Para `frame3_santa_base.mp4`:

- **Resolución:** 1080x1920 (vertical)
- **FPS:** 25
- **Codec:** H.264
- **Formato:** MP4 o MOV
- **Audio:** Sin audio (o audio que será reemplazado)
- **Duración:** Mínimo 15-20 segundos
- **Contenido:** Papá Noel estático, mirando a cámara, sin movimientos de boca

---

## Estructura de Carpetas

```
grido-backend/worker/
└── assets/
    ├── Frames_1_2_to_3.mov          ✅ Existe
    ├── frame3_santa_base.mp4        ❌ FALTA - Crear/exportar
    ├── Frame_4_NocheMagica.mov      ✅ Existe
    └── VideoReference.mp4           ✅ Existe (referencia)
```

---

## Notas Importantes

1. **`frame3_santa_base.mp4` es OPCIONAL:**
   - Solo se usa si usas Strategy 1 (TTS + Lip-sync)
   - Si usas Strategy 2 (HeyGen completo), no se necesita
   - El código tiene fallback: si no existe, usa el intro como base

2. **Si no tienes `frame3_santa_base.mp4`:**
   - El sistema funcionará igual
   - Usará el video de intro como base para lip-sync
   - Puede que el resultado no sea óptimo

3. **Para mejor resultado:**
   - Crea/exporta `frame3_santa_base.mp4` con Papá Noel estático
   - Asegúrate de que sea lo suficientemente largo (15-20 seg)
   - Sin audio o con audio que será reemplazado

---

## Cómo Crear/Exportar `frame3_santa_base.mp4`

1. **Desde tu diseño (Figma/After Effects/Photoshop):**
   - Exporta el frame 3 con Papá Noel estático
   - Sin animaciones de boca
   - Mirando a cámara
   - Duración: 15-20 segundos

2. **Especificaciones de exportación:**
   - Resolución: 1080x1920
   - FPS: 25
   - Codec: H.264
   - Formato: MP4
   - Sin audio

3. **Guardar en:**
   ```
   grido-backend/worker/assets/frame3_santa_base.mp4
   ```

---

## Verificación

Para verificar que todos los assets están en su lugar:

```bash
cd grido-backend/worker/assets
ls -lh
```

Deberías ver:
- ✅ `Frames_1_2_to_3.mov`
- ⚠️  `frame3_santa_base.mp4` (opcional)
- ✅ `Frame_4_NocheMagica.mov`


# Testing

Tests actuales:

- healthcheck API.
- creación de estudio mediante subida.
- validación de extensión.
- adapter con procesador dummy.
- detección de PDF generado.
- fallo de script externo.
- salida sin PDF.
- validación y generación de sujeto BIDS.
- preparación BIDS para un único T1w.
- adapter compneuro en modo simulado.
- búsqueda de `.nii` y `.nii.gz` en `Preproc`.
- generación de comandos FSL `slicer` sin ejecutar FSL real.
- generación de PDF técnico con PNG dummy y nombres de NIfTI.
- descarga del PDF técnico desde API.
- comportamiento sin NIfTI y con fallo de renderizado.
- generación de PDF técnico y ZIP.

Ejecutar:

```bash
make test
```

Lint Python:

```bash
make lint
```

Validación frontend:

```bash
cd frontend
npm install
npm run lint
```

El lint frontend usa `frontend/eslint.config.js`, compatible con ESLint 9. `package-lock.json` debe mantenerse actualizado cuando cambien dependencias frontend.

No se ejecuta build automáticamente por decisión del proyecto.

## Test Manual Lento

La ejecución real de `compneuro-anatproc` con `sub-O01_T1w.nii.gz` no forma parte de `make test`, porque puede tardar muchos minutos y requiere la imagen pesada. Debe probarse manualmente con:

```env
PROCESSOR_BACKEND=compneuro
WORKER_DOCKERFILE=worker/Dockerfile.compneuro
ALLOWED_EXTENSIONS=.nii.gz
MAX_CONCURRENT_PROCESSING_JOBS=1
```

Fichero de referencia local: `compneuro-anatproc/data/sub-O01/anat/sub-O01_T1w.nii.gz`.

Si esa carpeta local no existe, usar cualquier T1w `.nii.gz` anonimizado disponible. `compneuro-anatproc/` no es una dependencia permanente del proyecto; la integración real usa la imagen Docker configurada.

## Prueba Manual Realizada

En una prueba local con el worker compneuro reconstruido se procesó un T1w `.nii.gz` de ejemplo. El estudio terminó en estado `completed`, generó `output/Preproc`, 18 PNG en `output/rendered_png/`, `output/reports/technical_report.pdf` y `output/outputs.zip`, sin avisos de renderizado registrados.

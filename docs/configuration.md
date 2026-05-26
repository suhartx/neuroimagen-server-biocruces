# Configuración

La configuración local se define copiando `.env.example` a `.env` y ajustando sus valores antes de levantar los servicios.

```bash
cp .env.example .env
```

El fichero `.env` no debe commitearse. Puede contener contraseñas, rutas locales o comandos específicos del entorno.

## Variables Principales

| Variable | Uso | Valor por defecto |
| --- | --- | --- |
| `ENVIRONMENT` | Nombre del entorno de ejecución. | `development` |
| `POSTGRES_DB` | Base de datos creada por el contenedor PostgreSQL. | `neuroimagen` |
| `POSTGRES_USER` | Usuario de PostgreSQL. | `neuroimagen` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL. Debe cambiarse fuera de desarrollo. | `neuroimagen` |
| `DATABASE_URL` | URL usada por API y worker para conectarse a PostgreSQL. | `postgresql+psycopg://neuroimagen:neuroimagen@postgres:5432/neuroimagen` |
| `CELERY_BROKER_URL` | Broker Redis usado por Celery para encolar tareas. | `redis://redis:6379/0` |
| `CELERY_RESULT_BACKEND` | Backend Redis usado por Celery para resultados técnicos. | `redis://redis:6379/1` |
| `STORAGE_ROOT` | Ruta interna donde se guardan estudios, resultados y logs. | `/app/data/studies` |
| `ALLOWED_EXTENSIONS` | Extensiones aceptadas en la subida de estudios. | `.nii,.nii.gz,.dcm,.zip,.tar,.tar.gz,.gz,.json,.txt` |
| `MAX_UPLOAD_SIZE_MB` | Tamaño máximo de fichero permitido, en MB. | `1024` |
| `PROCESSOR_NAME` | Nombre técnico del procesador configurado. | `dummy-development-processor` |
| `PROCESSOR_VERSION` | Versión técnica del procesador configurado. | `0.1.0` |
| `PROCESSOR_BACKEND` | Backend activo: `dummy` o `compneuro`. | `dummy` |
| `PROCESSOR_COMMAND` | Comando CLI invocado por `processor_adapter`. | Dummy de desarrollo |
| `WORKER_DOCKERFILE` | Dockerfile usado para construir el worker. | `backend/Dockerfile` |
| `COMPNEURO_CONTAINER_IMAGE` | Imagen base documentada para trazabilidad de compneuro. | `compneurobilbaolab/compneuro-anatproc:1.1` |
| `COMPNEURO_ANATPROC_REF` | Commit del repo externo usado al construir el worker compneuro. | `a2f3e7c9523ed521c3f85f7dffde5ee8fb400842` |
| `COMPNEURO_PROJECT_MOUNT` | Ruta que el pipeline externo ve como proyecto. | `/project` |
| `COMPNEURO_COMMAND` | Comando ejecutado por el adapter compneuro. | `bash /app/src/apreproc_launcher.sh` |
| `PROCESSING_TIMEOUT_SECONDS` | Timeout del procesador; `0` lo desactiva. | `0` |
| `MAX_CONCURRENT_PROCESSING_JOBS` | Concurrencia del worker. Para compneuro se recomienda `1`. | `1` |
| `GENERATE_OUTPUT_ZIP` | Generar ZIP de outputs `Preproc`. | `true` |
| `GENERATE_TECHNICAL_PDF` | Generar PDF técnico de procesamiento. | `true` |
| `GENERATE_RENDERED_PNG` | Renderizar outputs NIfTI a PNG tras `compneuro`. | `true` |
| `NIFTI_RENDERER` | Herramienta CLI de renderizado. En compneuro debe ser FSL `slicer`. | `slicer` |
| `NIFTI_RENDER_MAX_FILES` | Máximo de NIfTI a renderizar por estudio. | `50` |
| `NIFTI_RENDER_TIMEOUT_SECONDS` | Timeout por fichero renderizado. | `300` |
| `TECHNICAL_REPORT_FILENAME` | Nombre del PDF dentro de `output/reports/`. | `technical_report.pdf` |
| `BIDS_VALIDATE` | Reservado para validación BIDS formal futura. | `false` |
| `CORS_ORIGINS` | Orígenes permitidos para llamadas desde navegador. | `http://localhost,http://localhost:5173` |

## `PROCESSOR_COMMAND`

`PROCESSOR_COMMAND` es la frontera con el script externo de procesamiento. No hay que acoplar la API ni el worker al script clínico: el worker siempre invoca `processor_adapter`, y el adaptador ejecuta este comando.

Ejemplo:

```env
PROCESSOR_COMMAND=python /app/external_processor/process.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

Placeholders disponibles:

- `{input_dir}`: directorio con el fichero subido.
- `{output_dir}`: directorio donde el script debe generar el PDF.
- `{study_id}`: identificador UUID del estudio.
- `{logs_dir}`: directorio reservado para logs técnicos.

El script configurado debe generar al menos un fichero `.pdf` dentro de `output_dir`. Si no lo hace, el procesamiento se marca como fallido.

## `PROCESSOR_BACKEND=compneuro`

La integración real ejecuta `compneuro-anatproc` dentro del worker, no mediante Docker-in-Docker. Configuración mínima:

```env
PROCESSOR_BACKEND=compneuro
PROCESSOR_NAME=compneuro-anatproc
PROCESSOR_VERSION=1.1
WORKER_DOCKERFILE=worker/Dockerfile.compneuro
ALLOWED_EXTENSIONS=.nii.gz
MAX_CONCURRENT_PROCESSING_JOBS=1
GENERATE_OUTPUT_ZIP=true
GENERATE_TECHNICAL_PDF=true
GENERATE_RENDERED_PNG=true
NIFTI_RENDERER=slicer
```

La API prepara automáticamente BIDS para un único sujeto T1w. Si el sujeto se deja vacío, genera un identificador seguro. Si se informa un valor inválido, responde `400`.

La carpeta local `compneuro-anatproc/` no es necesaria para ejecutar la integración. Puede existir como referencia temporal ignorada por Git, pero el flujo soportado usa la imagen Docker y `worker/Dockerfile.compneuro`.

## Seguridad Operativa

- No commitear `.env`.
- No poner secretos reales en `.env.example`.
- Cambiar `POSTGRES_PASSWORD` fuera de desarrollo local.
- No usar datos clínicos reales en pruebas o ejemplos.
- Mantener `ALLOWED_EXTENSIONS` limitado a formatos esperados.
- Revisar `MAX_UPLOAD_SIZE_MB` según capacidad de disco y política operativa.
- Si cambia `PROCESSOR_COMMAND`, reiniciar `api` y `worker`.

## Relación Con Docker Compose

`docker-compose.yml` lee estas variables y aplica valores por defecto si no están definidas. En desarrollo local suele bastar con crear `.env` desde `.env.example`; en despliegues reales hay que revisar contraseñas, rutas, CORS y comando del procesador antes de levantar servicios.

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
| `PROCESSOR_COMMAND` | Plantilla de comando usada por el backend `dummy`. | Dummy de desarrollo |
| `WORKER_DOCKERFILE` | Dockerfile usado para construir el worker. | `backend/Dockerfile` |
| `COMPNEURO_CONTAINER_IMAGE` | Imagen base documentada para trazabilidad de compneuro. | `compneurobilbaolab/compneuro-anatproc:1.1` |
| `COMPNEURO_ANATPROC_REF` | Commit del repo externo usado al construir el worker compneuro. | `a2f3e7c9523ed521c3f85f7dffde5ee8fb400842` |
| `COMPNEURO_PROJECT_MOUNT` | Ruta que el procesador externo ve como proyecto. | `/project` |
| `COMPNEURO_COMMAND` | Comando ejecutado por el adapter compneuro. | `bash /app/src/apreproc_launcher.sh` |
| `PROCESSING_TIMEOUT_SECONDS` | Timeout del procesador; `0` lo desactiva. | `0` |
| `MAX_CONCURRENT_PROCESSING_JOBS` | Concurrencia del worker. Para compneuro se recomienda `1`. | `1` |
| `GENERATE_OUTPUT_ZIP` | Generar ZIP de resultados `Preproc`. | `true` |
| `GENERATE_TECHNICAL_PDF` | Generar PDF técnico de procesamiento. | `true` |
| `GENERATE_RENDERED_PNG` | Renderizar resultados NIfTI a PNG tras `compneuro`. | `true` |
| `NIFTI_RENDERER` | Herramienta CLI de renderizado. En compneuro debe ser FSL `slicer`. | `slicer` |
| `NIFTI_RENDER_MAX_FILES` | Máximo de NIfTI a renderizar por estudio. | `50` |
| `NIFTI_RENDER_TIMEOUT_SECONDS` | Timeout por fichero renderizado. | `300` |
| `TECHNICAL_REPORT_FILENAME` | Nombre del PDF dentro de `output/reports/`. | `technical_report.pdf` |
| `BIDS_VALIDATE` | Reservado para validación BIDS formal futura. | `false` |
| `CORS_ORIGINS` | Orígenes permitidos para llamadas desde navegador. | `http://localhost,http://localhost:5173` |
| `AUTH_SECRET_KEY` | Clave HMAC para firmar tokens JWT. Debe cambiarse fuera de desarrollo. | `change-me-in-production` |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token local. | `480` |

## Usuario Admin Inicial

No hay registro público abierto. Tras aplicar migraciones, crear o actualizar el primer admin con:

```bash
make create-admin EMAIL=admin@example.org
```

El comando solicita la contraseña por consola y ejecuta `python -m app.cli.create_admin` dentro del contenedor `api`.

La autenticación local usa JWT firmado con `AUTH_SECRET_KEY`. En desarrollo existe un valor por defecto, pero en cualquier entorno compartido debe configurarse una clave propia y no commitearla. La API rechaza arrancar fuera de `development` si la clave sigue siendo el valor por defecto o es demasiado corta.

## `PROCESSOR_COMMAND`

`PROCESSOR_COMMAND` es la plantilla de comando para el procesador de desarrollo (`PROCESSOR_BACKEND=dummy`). No hay que acoplar la API ni el worker al script externo: el worker siempre invoca `processor_adapter`, y el adaptador decide qué comando ejecutar según el backend activo.

En modo `dummy`, el adaptador ejecuta `PROCESSOR_COMMAND`. En modo `compneuro`, el adaptador no usa `PROCESSOR_COMMAND` como comando principal, sino `COMPNEURO_COMMAND`.

Ejemplo:

```env
PROCESSOR_COMMAND=python /app/external_processor/dummy_processor.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

Placeholders disponibles:

- `{input_dir}`: directorio con el fichero subido.
- `{output_dir}`: directorio donde el script debe generar el PDF.
- `{study_id}`: identificador UUID del estudio.
- `{logs_dir}`: directorio reservado para logs técnicos.

En modo `dummy`, el script configurado debe generar al menos un fichero `.pdf` dentro de `output_dir`. Si no lo hace, el procesamiento se marca como fallido.

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

En este modo el comando principal es `COMPNEURO_COMMAND`, por defecto `bash /app/src/apreproc_launcher.sh`. El worker se construye sobre `compneurobilbaolab/compneuro-anatproc:1.1`, por lo que ejecuta el launcher y FSL `slicer` dentro del mismo contenedor worker.

`COMPNEURO_COMMAND` es el punto configurable para cambiar de script manteniendo el backend `compneuro`. Si el nuevo procesador requiere otras dependencias, el cambio debe acompañarse con otro `WORKER_DOCKERFILE` o con una imagen base distinta. El contenedor resultante sigue siendo el servicio `worker`: debe tener Celery, las dependencias Python de la plataforma, acceso a `/app/data` y el comando configurado disponible dentro del contenedor.

Para sustituir el procesador de forma más amplia, revisar:

- `PROCESSOR_BACKEND`: backend activo que selecciona el adapter.
- `COMPNEURO_COMMAND` o el comando equivalente del nuevo backend.
- `WORKER_DOCKERFILE`: Dockerfile que construye el worker con las herramientas necesarias.
- `COMPNEURO_CONTAINER_IMAGE`/imagen base documentada, si se mantiene este backend.
- estructura de resultados esperada por `worker/tasks.py` y `processor_adapter/output_packager.py`.

La API prepara automáticamente BIDS para un único sujeto T1w. Si el sujeto se deja vacío, genera un identificador seguro. Si se informa un valor inválido, responde `400`.

La carpeta local `compneuro-anatproc/` no es necesaria para ejecutar la integración. Puede existir como referencia temporal ignorada por Git, pero el flujo soportado usa la imagen Docker y `worker/Dockerfile.compneuro`.

## Cómo Sustituir El Procesador

Para cambiar la imagen Docker o usar otro script, mantén la separación entre plataforma y procesador externo:

1. Crear o adaptar un Dockerfile de worker con Celery, las dependencias Python de la plataforma y las herramientas del nuevo procesador.
2. Configurar `WORKER_DOCKERFILE` para construir ese worker.
3. Configurar `COMPNEURO_COMMAND` si basta con cambiar el script dentro del backend `compneuro`, o crear un backend nuevo en `processor_adapter` si cambia la interfaz esperada.
4. Asegurar que el comando nuevo lea los datos preparados por la plataforma y escriba resultados en la salida esperada, idealmente `output/Preproc`.
5. Dejar que el worker genere los artefactos propios de la plataforma: `output/reports/technical_report.pdf` y `output/outputs.zip`.
6. Reconstruir y reiniciar `worker`; reiniciar `api` si cambia configuración compartida.

No hace falta modificar la GUI ni los endpoints de FastAPI si el nuevo procesador respeta la interfaz esperada descrita en `docs/processing-pipeline.md`.

## Seguridad Operativa

- No commitear `.env`.
- No poner secretos reales en `.env.example`.
- Cambiar `POSTGRES_PASSWORD` fuera de desarrollo local.
- No usar datos reales identificativos o sensibles en pruebas o ejemplos.
- Mantener `ALLOWED_EXTENSIONS` limitado a formatos esperados.
- Revisar `MAX_UPLOAD_SIZE_MB` según capacidad de disco y política operativa.
- Si cambia el comando del procesador o el Dockerfile del worker, reiniciar o reconstruir los servicios afectados.

## Relación Con Docker Compose

`docker-compose.yml` lee estas variables y aplica valores por defecto si no están definidas. En desarrollo local suele bastar con crear `.env` desde `.env.example`; en despliegues reales hay que revisar contraseñas, rutas, CORS y comando del procesador antes de levantar servicios.

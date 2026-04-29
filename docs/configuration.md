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
| `PROCESSOR_COMMAND` | Comando CLI invocado por `processor_adapter`. | Dummy de desarrollo |
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

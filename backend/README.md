# Backend

Esta carpeta contiene la API HTTP del sistema. Está implementada con FastAPI y es responsable de recibir estudios, validarlos, registrar metadatos en PostgreSQL, encolar tareas Celery y servir la descarga del PDF generado.

## Responsabilidad

- Exponer endpoints REST bajo `/api`.
- Publicar documentación OpenAPI en `/api/docs`.
- Validar extensiones, tamaño y nombres de fichero.
- Guardar entradas en `data/studies/{study_id}/input`.
- Crear registros `Study`, `ProcessingJob` y `AuditEvent`.
- Encolar el procesamiento asíncrono.
- Descargar el PDF cuando el worker lo haya generado.

## Estructura Del Código

- `app/main.py`: crea la aplicación FastAPI, configura CORS y registra las rutas.
- `app/api/routes.py`: define los endpoints HTTP. Es la capa de entrada de la API y no ejecuta procesamiento pesado.
- `app/core/config.py`: centraliza configuración por variables de entorno usando `pydantic-settings`.
- `app/db/base.py`: define la clase base declarativa de SQLAlchemy.
- `app/db/session.py`: crea el engine, la sesión y la dependencia `get_db`.
- `app/models/`: contiene las tablas persistentes.
- `app/schemas/`: contiene modelos Pydantic para respuestas HTTP.
- `app/services/`: contiene lógica auxiliar de almacenamiento, auditoría y seguridad.
- `alembic/`: contiene migraciones de base de datos.
- `requirements.txt`: dependencias Python compartidas por API y worker.
- `Dockerfile`: imagen usada por `api` y `worker`.

## Modelos Principales

- `Study`: representa el estudio subido, sus rutas, estado y metadatos técnicos.
- `ProcessingJob`: representa una ejecución concreta del procesamiento asíncrono.
- `AuditEvent`: registra eventos relevantes para trazabilidad.

## Flujo De Subida

1. `POST /api/studies/upload` recibe un `UploadFile`.
2. `validate_upload` sanitiza y valida el nombre.
3. `LocalStudyStorage.save_upload` guarda el fichero y calcula tamaño/checksum.
4. Se crean `Study` y `ProcessingJob` con estado `queued`.
5. Se registra auditoría con `record_event`.
6. Se llama a `process_study.delay(...)` para delegar el trabajo al worker.

## Límites Arquitectónicos

La API no debe importar ni conocer detalles del algoritmo clínico. La ejecución real se delega al worker y siempre pasa por `processor_adapter`.

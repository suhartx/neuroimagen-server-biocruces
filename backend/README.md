# Backend

Esta carpeta contiene la API HTTP del sistema. Está implementada con FastAPI y es responsable de autenticar usuarios, recibir estudios, validarlos, registrar metadatos en PostgreSQL, encolar tareas Celery y servir descargas según permisos.

## Responsabilidad

- Exponer endpoints REST bajo `/api`.
- Publicar documentación OpenAPI en `/api/docs`.
- Autenticar usuarios con login local y JWT.
- Aplicar roles `admin`/`researcher` y propietario por estudio.
- Validar extensiones, tamaño y nombres de fichero.
- Guardar entradas en `data/studies/{study_id}/input`.
- Crear registros `Study`, `ProcessingJob` y `AuditEvent`.
- Encolar el procesamiento asíncrono.
- Descargar el PDF cuando el worker lo haya generado.
- Crear usuarios desde admin y permitir la creación del admin inicial por CLI.

## Estructura Del Código

- `app/main.py`: crea la aplicación FastAPI, configura CORS y registra las rutas.
- `app/api/routes.py`: define los endpoints HTTP. Es la capa de entrada de la API y no ejecuta procesamiento pesado.
- `app/cli/create_admin.py`: comando para crear o actualizar el admin inicial.
- `app/core/config.py`: centraliza configuración por variables de entorno usando `pydantic-settings`.
- `app/db/base.py`: define la clase base declarativa de SQLAlchemy.
- `app/db/session.py`: crea el engine, la sesión y la dependencia `get_db`.
- `app/models/`: contiene las tablas persistentes.
- `app/schemas/`: contiene modelos Pydantic para respuestas HTTP.
- `app/services/`: contiene lógica auxiliar de almacenamiento, auditoría, seguridad de subida y autenticación.
- `alembic/`: contiene migraciones de base de datos.
- `requirements.txt`: dependencias Python compartidas por API y worker.
- `Dockerfile`: imagen usada por `api` y `worker`.

## Modelos Principales

- `User`: representa usuarios locales con rol `admin` o `researcher`.
- `Study`: representa el estudio subido, sus rutas, estado y metadatos técnicos.
- `ProcessingJob`: representa una ejecución concreta del procesamiento asíncrono.
- `AuditEvent`: registra eventos relevantes para trazabilidad.

## Flujo De Subida

1. El usuario obtiene token con `POST /api/auth/login`.
2. `POST /api/studies/upload` recibe un `UploadFile` autenticado.
3. `validate_upload` sanitiza y valida el nombre.
4. `LocalStudyStorage.save_upload` guarda el fichero y calcula tamaño/checksum.
5. Se crean `Study` con `owner_user_id` y `ProcessingJob` con estado `queued`.
6. Se registra auditoría con `record_event` y usuario actor.
7. Se llama a `process_study.delay(...)` para delegar el trabajo al worker.

## Límites Arquitectónicos

La API no debe importar ni conocer detalles del algoritmo clínico. La ejecución real se delega al worker y siempre pasa por `processor_adapter`.

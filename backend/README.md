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
- Exponer detalle de jobs, logs truncados, cancelación de jobs en cola, retry de fallidos y borrado seguro.
- Exponer dashboard admin con métricas agregadas, healthchecks y alertas básicas.

## Estructura Del Código

- `app/main.py`: crea la aplicación FastAPI, configura CORS y registra las rutas.
- `app/api/routes.py`: define los endpoints HTTP. Es la capa de entrada de la API y no ejecuta procesamiento pesado.
- `app/schemas/admin.py`: contratos Pydantic del dashboard admin.
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

## Gestión De Jobs

- `GET /api/studies/{study_id}/detail`: estudio y jobs asociados.
- `GET /api/studies/{study_id}/logs`: `processor.log` y `rendering.log` truncados.
- `POST /api/studies/{study_id}/cancel`: cancela solo jobs en cola.
- `POST /api/studies/{study_id}/retry`: reencola estudios fallidos.
- `DELETE /api/studies/{study_id}`: soft delete y borrado físico si no está procesando.

## Dashboard Admin

- `GET /api/admin/dashboard`: resumen global solo para `admin`.
- Agrega cola, jobs por estado, usuarios, estudios por estado, almacenamiento, healthchecks y alertas.
- No invoca procesamiento ni accede al procesador externo; solo consulta DB, Redis, worker y filesystem.

## Límites Arquitectónicos

La API no debe importar ni conocer detalles internos del procesador externo. La ejecución real se delega al worker y siempre pasa por `processor_adapter`.

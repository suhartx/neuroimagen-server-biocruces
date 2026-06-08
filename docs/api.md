# API

Swagger está disponible en `/api/docs`.

## Endpoints

- `GET /api/health`: healthcheck.
- `POST /api/auth/login`: login local con email y contraseña.
- `POST /api/auth/logout`: registrar cierre de sesión cliente.
- `GET /api/auth/me`: usuario autenticado actual.
- `GET /api/admin/dashboard`: resumen operativo global. Solo admin.
- `GET /api/users`: listar usuarios. Solo admin.
- `POST /api/users`: crear usuario. Solo admin.
- `POST /api/studies/upload`: subir fichero y encolar procesamiento. Requiere autenticación.
- `GET /api/studies`: listar estudios visibles. Admin ve todos; researcher solo los propios.
- `GET /api/studies/{study_id}`: detalle si el usuario tiene permiso.
- `GET /api/studies/{study_id}/detail`: detalle extendido con jobs asociados.
- `GET /api/studies/{study_id}/status`: estado si el usuario tiene permiso.
- `GET /api/studies/{study_id}/logs`: logs técnicos truncados si el usuario tiene permiso.
- `POST /api/studies/{study_id}/cancel`: cancelar job en cola.
- `POST /api/studies/{study_id}/retry`: reintentar estudio fallido.
- `DELETE /api/studies/{study_id}`: soft delete en DB y borrado físico de ficheros si el estudio no está procesando.
- `GET /api/studies/{study_id}/download`: descargar PDF técnico si está completado. Alias compatible.
- `GET /api/studies/{study_id}/download/pdf`: descargar PDF técnico si el usuario tiene permiso.
- `GET /api/studies/{study_id}/download/zip`: descargar ZIP de outputs si existe y el usuario tiene permiso.

Salvo `GET /api/health` y `POST /api/auth/login`, los endpoints funcionales requieren `Authorization: Bearer <token>`.

## Autenticación

`POST /api/auth/login` usa JSON:

```json
{
  "email": "usuario@example.org",
  "password": "contraseña"
}
```

Respuesta:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "usuario@example.org",
    "full_name": "Usuario",
    "role": "researcher",
    "is_active": true
  }
}
```

Roles iniciales:

- `admin`: ve todos los estudios, crea usuarios y accede al dashboard operativo.
- `researcher`: sube estudios, lista y descarga solo los propios.

## Dashboard Admin

`GET /api/admin/dashboard` devuelve una foto operativa global para administración:

- cola: jobs en cola, procesando, fallidos y activos.
- usuarios: totales, activos, admins y researchers.
- estudios y jobs agrupados por estado.
- almacenamiento: ruta configurada, existencia, bytes registrados y disco libre/usado.
- servicios: PostgreSQL, Redis y Worker con estado `ok`, `warning`, `down` o `unknown`.
- últimos jobs fallidos.
- alertas básicas no bloqueantes.

Este endpoint no expone datos clínicos ni ejecuta procesamiento; agrega estado ya registrado en la plataforma.

## Subida

`POST /api/studies/upload` usa `multipart/form-data`:

- `file`: fichero de estudio.
- `bids_subject_id`: opcional, formato `sub-XXXX`, por ejemplo `sub-O01`.

Con `PROCESSOR_BACKEND=compneuro`, el fichero debe ser `.nii.gz` y la API prepara automáticamente `bids_project/data`.

Cada estudio queda asociado al usuario autenticado mediante `owner_user_id`.

## Gestión De Jobs

`GET /api/studies/{study_id}/detail` devuelve los metadatos del estudio y la lista de `ProcessingJob` asociados.

`GET /api/studies/{study_id}/logs?lines=200` devuelve, si existen, `processor.log` y `rendering.log` truncados a las últimas líneas solicitadas. El máximo permitido es 1000 líneas.

`POST /api/studies/{study_id}/cancel` solo funciona si el estudio está en estado `queued`. No cancela procesos ya iniciados.

`POST /api/studies/{study_id}/retry` solo funciona si el estudio está en estado `failed`. Crea un nuevo `ProcessingJob` y reencola el procesamiento.

`DELETE /api/studies/{study_id}` aplica soft delete con `deleted_at`, registra auditoría y borra físicamente la carpeta del estudio. Si el estudio está `processing`, responde `409`.

## Errores Esperados

- `400`: extensión no permitida.
- `400`: sujeto BIDS inválido.
- `401`: usuario no autenticado o token inválido.
- `403`: usuario autenticado sin permisos suficientes.
- `404`: estudio o PDF no encontrado.
- `404`: ZIP no disponible.
- `409`: operación no permitida para el estado actual del job.
- `413`: fichero demasiado grande.

## Extensiones Permitidas

La subida acepta las extensiones configuradas en `ALLOWED_EXTENSIONS`:

- `.nii`
- `.nii.gz`
- `.dcm`
- `.zip`
- `.tar`
- `.tar.gz`
- `.gz`
- `.json`
- `.txt`

Para `compneuro`, configurar `ALLOWED_EXTENSIONS=.nii.gz`.

# API

Swagger está disponible en `/api/docs`.

## Endpoints

- `GET /api/health`: healthcheck.
- `POST /api/auth/login`: login local con correo electrónico y contraseña.
- `POST /api/auth/logout`: registrar cierre de sesión cliente.
- `GET /api/auth/me`: usuario autenticado actual.
- `GET /api/me/notification-preferences`: preferencias de correo del usuario autenticado.
- `PATCH /api/me/notification-preferences`: actualizar preferencias de correo del usuario autenticado.
- `GET /api/notifications`: listar notificaciones internas del usuario autenticado.
- `POST /api/notifications/{notification_id}/read`: marcar una notificación propia como leída.
- `GET /api/admin/dashboard`: resumen operativo global. Solo admin.
- `GET /api/users`: listar usuarios. Solo admin.
- `POST /api/users`: crear usuario. Solo admin.
- `PATCH /api/users/{user_id}`: actualizar estado activo o cuota de almacenamiento. Solo admin.
- `DELETE /api/users/{user_id}`: borrar lógicamente un usuario. Solo admin.
- `POST /api/studies/upload`: subir fichero y encolar procesamiento. Requiere autenticación.
- `GET /api/studies`: listar estudios visibles. Admin ve todos; researcher solo los propios.
- `GET /api/studies/{study_id}`: detalle si el usuario tiene permiso.
- `GET /api/studies/{study_id}/detail`: detalle extendido con jobs asociados.
- `GET /api/studies/{study_id}/status`: estado si el usuario tiene permiso.
- `PATCH /api/studies/{study_id}/clinical-review`: marcar el resultado técnico como `technical_only`, `reviewed` o `validated`.
- `GET /api/studies/{study_id}/logs`: logs técnicos truncados si el usuario tiene permiso.
- `POST /api/studies/{study_id}/cancel`: cancelar job en cola o solicitar terminación de un procesamiento en ejecución.
- `POST /api/studies/{study_id}/retry`: reintentar estudio fallido.
- `DELETE /api/studies/{study_id}`: soft delete en DB y borrado físico de ficheros si el estudio no está procesando.
- `GET /api/studies/{study_id}/download`: descargar PDF técnico si está completado. Alias compatible.
- `GET /api/studies/{study_id}/download/pdf`: descargar PDF técnico si el usuario tiene permiso.
- `GET /api/studies/{study_id}/download/zip`: descargar ZIP de resultados si existe y el usuario tiene permiso.
- `POST /api/studies/{study_id}/share-links`: crear enlace temporal para descargar el PDF técnico. Requiere propietario o admin.
- `GET /api/studies/{study_id}/share-links`: listar enlaces compartidos de un estudio. Requiere propietario o admin.
- `POST /api/studies/{study_id}/share-links/{link_id}/revoke`: revocar un enlace compartido. Requiere propietario o admin.
- `GET /api/share/{token}/pdf`: descargar PDF técnico mediante token temporal, sin login.

Salvo `GET /api/health` y `POST /api/auth/login`, los endpoints funcionales requieren `Authorization: Bearer <token>`.

La excepción funcional adicional es `GET /api/share/{token}/pdf`: no requiere JWT porque el propio token opaco habilita una descarga temporal del PDF.

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

- `admin`: ve todos los estudios, gestiona usuarios/cuotas, accede al dashboard operativo y puede marcar revisión técnica.
- `researcher`: sube estudios, consulta cuota, lista y descarga solo los propios y puede marcar revisión técnica de sus estudios.

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

Si el usuario tiene `storage_quota_bytes` definido, la API rechaza la subida cuando el tamaño del nuevo fichero supera su cuota disponible.

## Gestión De Jobs

`GET /api/studies/{study_id}/detail` devuelve los metadatos del estudio y la lista de `ProcessingJob` asociados.

`GET /api/studies/{study_id}/logs?lines=200` devuelve, si existen, `processor.log` y `rendering.log` truncados a las últimas líneas solicitadas. El máximo permitido es 1000 líneas.

`POST /api/studies/{study_id}/cancel` funciona si el estudio está en estado `queued` o `processing`. En cola revoca la tarea pendiente y marca el estudio como `canceled`; durante procesamiento registra la solicitud, revoca la tarea Celery con `SIGTERM` y el worker/adaptador intentan propagar la cancelación al proceso externo. La respuesta inmediata puede seguir mostrando `processing` hasta que el worker cierre la tarea.

`POST /api/studies/{study_id}/retry` solo funciona si el estudio está en estado `failed`. Crea un nuevo `ProcessingJob` y reencola el procesamiento.

`DELETE /api/studies/{study_id}` aplica soft delete con `deleted_at`, registra auditoría y borra físicamente la carpeta del estudio. Si el estudio está `processing`, responde `409`.

## Compartición De Informes

`POST /api/studies/{study_id}/share-links` crea un enlace temporal para un estudio completado con PDF disponible. El body es opcional:

```json
{
  "expires_in_hours": 72
}
```

La respuesta incluye el enlace completo solo en el momento de creación:

```json
{
  "id": "...",
  "study_id": "...",
  "url": "http://localhost/api/share/<token>/pdf",
  "created_at": "...",
  "expires_at": "...",
  "revoked_at": null,
  "last_accessed_at": null,
  "access_count": 0,
  "is_expired": false,
  "is_revoked": false
}
```

El token no se almacena en claro: la base de datos guarda solo un hash. `GET /api/studies/{study_id}/share-links` lista metadatos de enlaces, pero no puede recuperar tokens ya creados. Si se pierde un enlace, hay que revocarlo o crear uno nuevo.

`GET /api/share/{token}/pdf` descarga únicamente el PDF técnico si el token existe, no caducó y no fue revocado. Tokens inválidos, caducados o revocados responden `404` para no facilitar enumeración.

Cada creación, revocación y descarga por token queda registrada en auditoría.

## Errores Esperados

- `400`: extensión no permitida.
- `400`: sujeto BIDS inválido.
- `401`: usuario no autenticado o token inválido.
- `403`: usuario autenticado sin permisos suficientes.
- `404`: estudio o PDF no encontrado.
- `404`: ZIP no disponible.
- `404`: enlace público inválido, caducado o revocado.
- `409`: operación no permitida para el estado actual del job.
- `409`: intento de compartir un estudio sin PDF completado.
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

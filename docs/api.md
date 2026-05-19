# API

Swagger está disponible en `/api/docs`.

## Endpoints

- `GET /api/health`: healthcheck.
- `POST /api/studies/upload`: subir fichero y encolar procesamiento.
- `GET /api/studies`: listar estudios.
- `GET /api/studies/{study_id}`: detalle.
- `GET /api/studies/{study_id}/status`: estado.
- `GET /api/studies/{study_id}/download`: descargar PDF técnico si está completado. Alias compatible.
- `GET /api/studies/{study_id}/download/pdf`: descargar PDF técnico.
- `GET /api/studies/{study_id}/download/zip`: descargar ZIP de outputs si existe.

## Subida

`POST /api/studies/upload` usa `multipart/form-data`:

- `file`: fichero de estudio.
- `bids_subject_id`: opcional, formato `sub-XXXX`, por ejemplo `sub-O01`.

Con `PROCESSOR_BACKEND=compneuro`, el fichero debe ser `.nii.gz` y la API prepara automáticamente `bids_project/data`.

## Errores Esperados

- `400`: extensión no permitida.
- `400`: sujeto BIDS inválido.
- `404`: estudio o PDF no encontrado.
- `404`: ZIP no disponible.
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

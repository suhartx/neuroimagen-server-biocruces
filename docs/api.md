# API

Swagger está disponible en `/api/docs`.

## Endpoints

- `GET /api/health`: healthcheck.
- `POST /api/studies/upload`: subir fichero y encolar procesamiento.
- `GET /api/studies`: listar estudios.
- `GET /api/studies/{study_id}`: detalle.
- `GET /api/studies/{study_id}/status`: estado.
- `GET /api/studies/{study_id}/download`: descargar PDF si está completado.

## Errores Esperados

- `400`: extensión no permitida.
- `404`: estudio o PDF no encontrado.
- `413`: fichero demasiado grande.

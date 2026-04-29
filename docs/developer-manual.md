# Manual De Desarrollo

## Entorno Local

```bash
cp .env.example .env
make up
make test
```

El significado de cada variable de `.env` está documentado en `docs/configuration.md`.

## Backend

- FastAPI en `backend/app`.
- Modelos en `backend/app/models`.
- Migraciones Alembic en `backend/alembic`.

## Worker

- Celery en `worker/`.
- No añadir lógica clínica al worker; usar `processor_adapter`.

## Frontend

- React/Vite en `frontend/`.
- UI sencilla, castellano, clara y sin flujos clínicos no implementados.

## Convenciones

- Conventional Commits.
- Actualizar tests ante cambios funcionales.
- Actualizar docs si cambia arquitectura, API, despliegue o pipeline.

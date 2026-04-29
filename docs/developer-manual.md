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
- Instalar dependencias con `npm install` desde `frontend/`; el `package-lock.json` fija las versiones resueltas para reproducibilidad.
- Validar cambios frontend con `npm run lint`; la configuración vive en `frontend/eslint.config.js` y usa el formato flat config de ESLint 9.

## Convenciones

- Conventional Commits.
- Actualizar tests ante cambios funcionales.
- Actualizar docs si cambia arquitectura, API, despliegue o pipeline.
- Documentar cambios de tooling frontend cuando afecten instalación, lint o estructura de componentes.

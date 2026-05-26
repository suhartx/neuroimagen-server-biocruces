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
- `worker/Dockerfile.compneuro` construye el worker real sobre la imagen de `compneuro-anatproc` y añade dependencias de la plataforma.
- El post-procesado técnico corre en el mismo worker: renderiza NIfTI con FSL `slicer`, genera PDF y empaqueta outputs.
- La concurrencia recomendada para `compneuro` es `1`, porque el pipeline usa `/project` como ruta fija.

## Processor Adapter

- `processor_adapter.adapter.DummyProcessorAdapter`: mantiene el procesador de desarrollo con PDF.
- `processor_adapter.adapter.CompneuroAnatprocAdapter`: prepara `/project`, ejecuta `src/apreproc_launcher.sh` y valida `Preproc/BET` y `Preproc/ProbTissue`.
- `processor_adapter.nifti_renderer`: encuentra `.nii`/`.nii.gz` en `Preproc` y ejecuta `slicer input -a output.png`.
- `processor_adapter.technical_pdf_report`: genera el PDF técnico con metadatos, listado de outputs y PNG renderizados.
- `processor_adapter.output_packager`: genera el ZIP de outputs con rutas relativas.
- `processor_adapter.artifacts`: puente de compatibilidad para imports existentes.

## BIDS

- `backend/app/services/bids.py` prepara BIDS para un único T1w por estudio.
- No se usan sesiones BIDS en esta fase.
- `bids_subject_id` debe tener formato `sub-XXXX`; ejemplo: `sub-O01`.

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

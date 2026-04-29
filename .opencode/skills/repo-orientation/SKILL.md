---
name: repo-orientation
description: Explorar este repositorio sin perderse: fuentes de verdad, estructura, comandos y zonas sensibles.
compatibility: opencode
---

## Uso

Cargá esta skill cuando empieces una tarea en este repo o cuando necesites reconstruir contexto.

## Flujo

1. Leé `AGENTS.md`.
2. Para arquitectura, leé `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md`.
3. Confirmá comandos en `Makefile`, `backend/requirements.txt`, `frontend/package.json` y `docker-compose.yml`.
4. Ubicá el cambio en la carpeta correcta: `backend/`, `worker/`, `processor_adapter/`, `frontend/`, `infra/`, `docs/` o `.opencode/`.
5. Ignorá para contexto normal: `.git/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `node_modules/`, `dist/`, `data/studies/` y `.opencode/node_modules/`.

## Recordatorio

El procesador externo entra por `processor_adapter`. No metas lógica clínica en API ni worker.

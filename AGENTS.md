# AGENTS.md

Fuente principal para trabajar con agentes en este repositorio. OpenCode debe leer este archivo antes de tocar código o documentación.

## Propósito

TFM para una plataforma web de procesamiento asíncrono de neuroimagen. El valor está en la integración, trazabilidad, cola de trabajos y frontera con el procesador externo, no en reimplementar lógica clínica.

## Arquitectura

- `frontend/`: GUI React/Vite sencilla, en castellano, servida por Nginx.
- `backend/`: API FastAPI, SQLAlchemy, Alembic, validación de subida y descarga de PDF.
- `worker/`: tareas Celery que ejecutan procesos largos fuera del ciclo HTTP.
- `processor_adapter/`: frontera obligatoria con cualquier script externo.
- `external_processor/`: procesador dummy de desarrollo; no tiene validez clínica.
- `infra/reverse-proxy/`: Nginx como entrada HTTP.
- `data/studies/`: almacenamiento local de estudios, ignorado por Git.

Antes de cambios relevantes, revisá `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md`.

## Comandos

```bash
cp .env.example .env          # setup local, sin leer ni exponer .env
make up                       # levantar Docker Compose
make down                     # parar servicios
make test                     # pytest con PYTHONPATH local
make lint                     # ruff check backend/worker/adapter/tests
make format                   # ruff format backend/worker/adapter/tests
make check-docs               # docs obligatorios presentes
make check-secrets            # revisión básica de secretos
make smoke                    # healthcheck vía proxy
```

Frontend: `npm run dev`, `npm run lint`, `npm run format` y `npm run build` existen en `frontend/package.json`; ejecutalos desde `frontend/` solo cuando aplique.

## Reglas De Edición

- Cambios pequeños, revisables y alineados con la arquitectura existente.
- No acoplar API ni worker al algoritmo clínico: usar siempre `processor_adapter`.
- No modificar scripts clínicos reales sin autorización explícita.
- No añadir autenticación, roles, MinIO/S3, TLS, retención ni funcionalidades de roadmap salvo petición explícita.
- Mantener la GUI simple, clara y en castellano.
- No usar datos clínicos reales, identificativos ni fixtures sensibles.
- No introducir secretos ni leer `.env` salvo autorización explícita y necesidad real.
- No ejecutar deploys, pushes, migraciones destructivas, `make clean`, `rm -rf` ni comandos equivalentes sin permiso explícito.

## Validación

- Para cambios backend/worker/adapter: `make test` y `make lint`.
- Para documentación o reglas de agentes: `make check-docs` y revisar coherencia con `README.md`.
- Para seguridad/configuración: `make check-secrets` y revisar que `.env` siga ignorado.
- Revisar `git diff` antes de cerrar una tarea y explicar validaciones ejecutadas o pendientes.

## Documentación

- Actualizar docs junto con cambios que afecten arquitectura, API, despliegue, configuración, seguridad o pipeline.
- `AGENTS.md` es la fuente de verdad para agentes; `CLAUDE.md` queda como puente de compatibilidad.
- Registrar decisiones de flujo agentic en `docs/agentic-workflow-audit.md` cuando cambie `.opencode/`, agentes, skills, comandos o permisos.

## Git

- Usar Conventional Commits si el usuario pide commit.
- Mantener `develop` como rama de trabajo con configuración IA.
- Si el usuario pide push sin rama concreta, subir a `develop` y `main`; `main` debe quedar limpio sin `.claude/`, `.opencode/`, `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `docs/ai-development-rules.md` ni documentación agentic.
- `git push` está permitido solo bajo petición explícita del usuario; antes de cerrar, comprobar que `origin/main` no contiene archivos IA.

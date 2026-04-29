---
name: doc-sync
description: Mantener AGENTS.md, README y docs alineados con cambios reales sin crear documentación de relleno.
compatibility: opencode
---

## Uso

Cargá esta skill cuando cambien arquitectura, API, despliegue, configuración, seguridad, pipeline, agentes, skills, comandos o permisos.

## Reglas

- `AGENTS.md` es la fuente principal para agentes.
- `CLAUDE.md` es puente de compatibilidad y no debe contradecir `AGENTS.md`.
- `README.md` debe describir el uso principal y estructura real.
- `docs/architecture.md` y `docs/processing-pipeline.md` deben reflejar el flujo técnico actual.
- `docs/agentic-workflow-audit.md` registra decisiones sobre OpenCode, agentes, skills, comandos y plugins.

## Anti-relleno

No agregues docs nuevas si una sección corta en un documento existente alcanza. Si creás un archivo nuevo, explicá por qué existe.

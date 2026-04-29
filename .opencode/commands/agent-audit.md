---
description: Audita coherencia entre código, AGENTS.md, CLAUDE.md, .opencode y docs sin editar.
agent: project-architect
subtask: true
---

Auditá el flujo de agentes del repositorio.

Alcance:

- Compará `AGENTS.md`, `CLAUDE.md`, `.opencode/**`, `.claude/**`, `README.md` y `docs/**` contra código, tests, Makefile, Docker y scripts.
- Identificá contradicciones, documentación desactualizada, configuración inválida o redundante.
- No edites archivos salvo que el usuario lo pida explícitamente.
- Devolvé hallazgos priorizados, evidencia concreta y cambios mínimos recomendados.

Argumentos opcionales: `$ARGUMENTS`

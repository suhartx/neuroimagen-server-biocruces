# Agentic Workflow Audit

Fecha: 2026-04-29

## Estado Inicial

- Proyecto configurado para Claude Code y OpenCode.
- `AGENTS.md`, `CLAUDE.md` y `docs/ai-development-rules.md` repetían reglas parecidas.
- `.opencode/` tenía 7 agentes y 9 comandos muy breves, sin frontmatter útil para OpenCode actual.
- No existía `opencode.json` en la raíz.
- No había skills OpenCode en `.opencode/skills/<name>/SKILL.md`.
- `.opencode/node_modules/` existía localmente y debe permanecer ignorado.

## Stack Verificado

- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic Settings.
- Worker: Celery con Redis.
- Persistencia: PostgreSQL y filesystem local en `data/studies/`.
- Frontend: React/Vite servido por Nginx.
- Orquestación: Docker Compose y Makefile.

## Conflictos Detectados

- OpenCode estaba documentado como si tuviera agentes completos, pero los archivos eran descripciones de 3 líneas.
- Los comandos OpenCode eran copia conceptual de Claude y no representaban rutinas realmente repetibles.
- `CLAUDE.md` podía divergir de `AGENTS.md` al mantener una lista propia de reglas.
- Faltaba una configuración raíz con modelo, permisos defensivos e ignores de contexto.

## Decisiones Tomadas

- `AGENTS.md` queda como fuente principal para agentes.
- `CLAUDE.md` queda como puente de compatibilidad hacia `AGENTS.md`.
- OpenCode queda priorizado con `opencode.json` y modelo `openai/gpt-5.5`.
- Se reducen agentes a tres: arquitectura, documentación y revisión.
- Se reducen comandos a tres rutinas repetibles: auditoría, handoff y review de diff.
- Se crean tres skills bajo demanda: orientación, cambio seguro y sincronización documental.
- Se añade un plugin local simple para bloquear lecturas accidentales de secretos.
- Se permite `git push` bajo confirmación explícita (`ask`) para ejecutar el flujo acordado de subida a `develop` y `main` sin desactivar las protecciones restantes.

## Archivos Creados O Modificados

- `AGENTS.md`: reglas principales para agentes.
- `CLAUDE.md`: puente de compatibilidad.
- `opencode.json`: modelo, instrucciones, permisos e ignores.
- `.opencode/README.md`: estructura OpenCode real.
- `.opencode/.gitignore`: ignora dependencias generadas por OpenCode.
- `.opencode/agents/*.md`: agentes especializados mínimos.
- `.opencode/commands/*.md`: comandos repetibles mínimos.
- `.opencode/skills/*/SKILL.md`: skills reutilizables.
- `.opencode/plugins/secret-protection.js`: protección local de secretos.
- `docs/agentic-workflow-audit.md`: este registro.

## Uso De OpenCode

- Usar `AGENTS.md` como instrucciones base.
- Verificar el modelo disponible con `opencode models` si falla `openai/gpt-5.5`.
- Usar razonamiento alto para arquitectura, auditoría y reviews delicadas.
- Usar razonamiento medio y respuestas concisas para implementación normal.
- Mantener prompts pequeños: cargar skills solo cuando aporten contexto específico.

## Agentes

- `project-architect`: análisis profundo, diseño, riesgos y refactors delicados.
- `doc-steward`: documentación, handoffs y coherencia documental.
- `code-reviewer`: revisión read-only de cambios.

## Skills

- `repo-orientation`: exploración rápida del repo.
- `safe-change`: protocolo de cambio pequeño y validado.
- `doc-sync`: actualización documental sin relleno.

## Comandos

- `/agent-audit`: audita coherencia de configuración agentic sin editar.
- `/handoff`: resume estado, decisiones, validaciones y siguiente paso.
- `/review-diff`: revisa el diff actual sin editar.

## Hooks / Plugins

- `secret-protection.js`: bloquea lecturas de `.env`, credenciales, secretos y claves/certificados comunes.
- `opencode.json`: mantiene `git push*` en modo `ask`; no se permite push implícito ni force push sin autorización expresa.

## No Creado

- No se crearon agentes por backend/frontend/devops/qa/security porque las responsabilidades ya están cubiertas por `AGENTS.md`, skills bajo demanda y comandos existentes del proyecto.
- No se crearon comandos para `test` o `lint` porque el Makefile ya los expone claramente.
- No se añadieron plugins complejos porque aumentarían mantenimiento sin evidencia de necesidad.

## Riesgos Pendientes

- Confirmar con `opencode models` que `openai/gpt-5.5` está disponible con las credenciales locales.
- Revisar en uso real que los patrones de permisos de OpenCode bloquean todos los comandos sensibles esperados.
- Tras cada subida a `main`, comprobar que no existan `.claude/`, `.opencode/`, `AGENTS.md`, `CLAUDE.md`, `opencode.json`, `docs/ai-development-rules.md` ni documentación agentic.
- `.opencode/node_modules/` permanece localmente; no debe commitearse ni usarse como contexto.

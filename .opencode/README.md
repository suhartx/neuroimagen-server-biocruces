# OpenCode Config

Configuración mínima para trabajar con OpenCode + GPT-5.5 en este repositorio.

## Estructura

- `agents/`: subagentes especializados y con permisos defensivos.
- `skills/`: instrucciones reutilizables bajo demanda.
- `commands/`: rutinas repetibles de auditoría, handoff y review.
- `plugins/`: protecciones locales simples.

## Fuente De Verdad

`AGENTS.md` contiene las reglas generales del proyecto. Esta carpeta solo define herramientas OpenCode; no sustituye la arquitectura ni la documentación del TFM.

## Importante

Esta carpeta no forma parte del runtime Docker. Si OpenCode genera `node_modules`, `package.json`, `package-lock.json` o `bun.lock` dentro de `.opencode/`, no deben commitearse.

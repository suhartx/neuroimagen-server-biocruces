---
description: Revisa el diff actual contra AGENTS.md y convenciones del proyecto sin editar.
agent: code-reviewer
subtask: true
---

Revisá los cambios actuales del working tree.

Usá `AGENTS.md` como referencia principal y contrastá con el código real. Enfocate en:

- Bugs, regresiones y riesgos de seguridad.
- Secretos, `.env`, credenciales o datos clínicos reales.
- Desvíos de arquitectura o acoplamiento al procesador externo.
- Tests, docs o validaciones faltantes.
- Comandos peligrosos o permisos demasiado amplios.

No edites archivos. Devolvé hallazgos priorizados con referencias concretas. Si no hay hallazgos, decilo explícitamente.

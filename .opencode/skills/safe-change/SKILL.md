---
name: safe-change
description: Protocolo para cambios pequeños, reversibles y validados en este proyecto.
compatibility: opencode
---

## Uso

Cargá esta skill antes de modificar código, configuración o flujo de agentes.

## Protocolo

1. Entendé el estado actual leyendo los archivos mínimos necesarios.
2. Tocá la menor cantidad de archivos posible.
3. No reviertas cambios ajenos del working tree.
4. No leas `.env`, credenciales ni datos reales.
5. No ejecutes comandos destructivos, deploys, pushes, migraciones ni limpiezas sin permiso explícito.
6. Después de editar, revisá `git diff`.
7. Ejecutá validaciones enfocadas: `make test`, `make lint`, `make check-docs`, `make check-secrets` según el cambio.
8. Explicá qué se validó y qué queda pendiente.

## Criterio

Si una solución requiere compatibilidad hacia atrás, nuevas abstracciones o mucho código nuevo, primero justificá la necesidad con evidencia.

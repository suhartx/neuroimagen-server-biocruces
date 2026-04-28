# Claude Assistant Config

Esta carpeta contiene comandos y skills documentados para desarrollo asistido con Claude.

## Responsabilidad

- Guiar a asistentes IA para trabajar con las reglas del proyecto.
- Separar comandos reutilizables de instrucciones generales.
- Mantener especializaciones por rol técnico.

## Estructura Del Código

- `commands/`: instrucciones cortas para tareas frecuentes como planificar, revisar arquitectura, implementar endpoints o ejecutar checks.
- `skills/`: guías por especialidad: backend, frontend, DevOps, documentación, QA y seguridad.

## Relación Con El Proyecto

Estas instrucciones no son código ejecutable de la plataforma. Son documentación operativa para reducir errores cuando se trabaja con IA.

## Regla

Si cambia la arquitectura o las reglas del proyecto, esta carpeta debe mantenerse alineada con `CLAUDE.md`, `AGENTS.md` y `docs/ai-development-rules.md`.

# OpenCode Assistant Config

Esta carpeta contiene comandos y agentes documentados para desarrollo asistido con OpenCode.

## Responsabilidad

- Definir comandos reutilizables para tareas frecuentes.
- Definir agentes por rol: arquitectura, backend, frontend, DevOps, documentación, QA y seguridad.
- Mantener las reglas del repositorio disponibles para asistentes IA.

## Estructura Del Código

- `commands/`: guías para planificar features, revisar arquitectura, implementar endpoints, actualizar docs y preparar releases.
- `agents/`: descripciones de responsabilidades por agente.

## Importante

Esta carpeta no forma parte del runtime Docker. No interviene en la API, worker, frontend ni procesamiento clínico.

Si tu herramienta genera cachés o dependencias internas dentro de `.opencode`, no deben commitearse.

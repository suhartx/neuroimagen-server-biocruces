# CLAUDE.md

Compatibilidad para Claude Code. La fuente principal del repositorio es `AGENTS.md`; si hay conflicto, seguí `AGENTS.md` y el código verificable.

Reglas obligatorias:

1. Leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md` antes de cambios relevantes.
2. Mantener separación entre API, worker, frontend, infraestructura y documentación.
3. Integrar cualquier procesador mediante `processor_adapter`.
4. No modificar scripts clínicos reales sin autorización explícita.
5. No introducir secretos, no commitear `.env` y no usar datos clínicos reales.
6. Añadir o actualizar tests cuando haya cambios funcionales.
7. Actualizar documentación cuando cambie arquitectura, endpoints, despliegue, configuración o pipeline.
8. Ejecutar `make test`, `make lint`, `make check-docs` y `make check-secrets` cuando aplique.
9. Priorizar soluciones sencillas, mantenibles y revisables.

El procesador dummy en `external_processor/` es solo una herramienta de desarrollo y no tiene validez clínica.

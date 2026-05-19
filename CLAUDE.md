# CLAUDE.md

Compatibilidad para Claude Code. La fuente principal del repositorio es `AGENTS.md`; si hay conflicto, seguí `AGENTS.md` y el código verificable.

Reglas obligatorias:

1. Leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md` antes de cambios relevantes.
2. Mantener separación entre API, worker, frontend, infraestructura y documentación.
3. Integrar cualquier procesador mediante `processor_adapter`.
4. No modificar scripts clínicos reales sin autorización explícita.
5. Para `compneuro-anatproc`, tratar el repo externo como caja negra versionada y ejecutar solo `src/apreproc_launcher.sh` salvo autorización explícita.
6. No introducir secretos, no commitear `.env` y no usar datos clínicos reales.
7. Añadir o actualizar tests cuando haya cambios funcionales.
8. Actualizar documentación cuando cambie arquitectura, endpoints, despliegue, configuración o pipeline.
9. Ejecutar `make test`, `make lint`, `make check-docs` y `make check-secrets` cuando aplique.
10. Priorizar soluciones sencillas, mantenibles y revisables.

El procesador dummy en `external_processor/` es solo una herramienta de desarrollo y no tiene validez clínica.

# CLAUDE.md

Reglas obligatorias para trabajar en este repositorio:

1. Antes de implementar, leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md`.
2. Planificar cada cambio antes de tocar código.
3. No modificar el script real de procesamiento salvo autorización explícita.
4. Integrar cualquier procesador mediante `processor_adapter`.
5. Mantener separación entre API, worker, frontend, infraestructura y documentación.
6. Añadir o actualizar tests cuando haya cambios funcionales.
7. Actualizar documentación cuando cambie arquitectura, endpoints, despliegue o flujo.
8. Ejecutar `make test`, `make lint`, `make check-docs` y `make check-secrets` cuando aplique.
9. No introducir secretos ni commitear `.env`.
10. No usar datos clínicos reales en fixtures o ejemplos.
11. Priorizar soluciones sencillas y mantenibles.
12. Registrar decisiones relevantes en `docs/`.

El procesador dummy es solo una herramienta de desarrollo y no tiene validez clínica.

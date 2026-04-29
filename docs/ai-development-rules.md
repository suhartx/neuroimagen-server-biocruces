# Reglas De Desarrollo Con IA

`AGENTS.md` es la fuente principal para agentes. Este documento resume las reglas estables para la documentación general del TFM.

1. Leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md` antes de cambios relevantes.
2. No modificar scripts clínicos reales sin autorización explícita.
3. Integrar scripts externos mediante `processor_adapter`.
4. Mantener separación entre API, worker, frontend, infraestructura y documentación.
5. Añadir o actualizar tests cuando haya cambios funcionales.
6. Actualizar documentación cuando cambie arquitectura, endpoints, despliegue, configuración, seguridad o pipeline.
7. Ejecutar comprobaciones de calidad antes de cerrar una tarea.
8. No introducir secretos ni leer `.env` salvo necesidad autorizada.
9. No usar datos clínicos reales, identificativos ni fixtures sensibles.
10. Priorizar soluciones pequeñas, sencillas y mantenibles.
11. Registrar cambios de flujo agentic en `docs/agentic-workflow-audit.md`.

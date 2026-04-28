# Reglas De Desarrollo Con IA

1. Leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md` antes de implementar.
2. Planificar cada cambio antes de tocar código.
3. No modificar el script real de procesamiento salvo autorización explícita.
4. Integrar scripts mediante `processor_adapter`.
5. Mantener separación entre API, worker, frontend, infraestructura y documentación.
6. Añadir o actualizar tests cuando haya cambios funcionales.
7. Actualizar documentación cuando cambie arquitectura, endpoints, despliegue o flujo.
8. Ejecutar comprobaciones de calidad antes de cerrar una tarea.
9. No introducir secretos.
10. No usar datos clínicos reales en fixtures o ejemplos.
11. Priorizar soluciones sencillas y mantenibles.
12. Registrar decisiones relevantes en documentación.

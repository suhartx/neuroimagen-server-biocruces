# Roadmap

## Milestones Iniciales

- Milestone 0: preparación del repositorio, README, estructura y documentación base.
- Milestone 1: Docker Compose mínimo con PostgreSQL, Redis, API, worker, frontend y proxy.
- Milestone 2: backend FastAPI, PostgreSQL, SQLAlchemy y migraciones.
- Milestone 3: subida y almacenamiento local de estudios.
- Milestone 4: cola Redis y Celery worker.
- Milestone 5: adaptador CLI para script Python externo.
- Milestone 6: GUI simple en castellano.
- Milestone 7: descarga del PDF.
- Milestone 8: logs, auditoría básica y trazabilidad.
- Milestone 9: tests básicos y scripts de validación.
- Milestone 10: documentación final para TFM.
- Milestone 11: renderizado técnico de NIfTI a PNG con FSL `slicer` y PDF técnico con imágenes.

## Evolución Futura

- Futuro 1: autenticación local.
- Futuro 2: roles usuario/administrador.
- Futuro 3: historial por usuario.
- Futuro 4: múltiples scripts o herramientas de procesamiento.
- Futuro 5: gestión de herramientas Python desde panel admin.
- Futuro 6: MinIO/S3 y abstracción real de objetos.
- Futuro 7: TLS real, cabeceras de seguridad y hardening.
- Futuro 8: integración hospitalaria con sistemas internos.
- Futuro 9: notificaciones.
- Futuro 10: Jenkins/CI-CD.
- Futuro 11: Prometheus, Grafana y Loki.
- Futuro 12: políticas de retención y archivado.
- Futuro 13: revisión clínica y validación de informes.
- Futuro 14: sesiones BIDS y múltiples sujetos por estudio.
- Futuro 15: ejecutar `utils/brainmeasures.sh` después de `apreproc_launcher.sh`.
- Futuro 16: múltiples pipelines seleccionables por estudio.
- Futuro 17: validación BIDS formal con `bids-validator` si el coste operativo queda justificado.
- Futuro 18: selección más fina de outputs relevantes para el PDF según criterios de revisión técnica.

## Criterio Arquitectónico

La prioridad es mantener una base simple, auditable y defendible. Las capacidades clínicas y hospitalarias reales requieren validación, seguridad, trazabilidad y gobierno de datos adicionales.

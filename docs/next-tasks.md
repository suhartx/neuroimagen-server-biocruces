# Proximas Tareas

Este documento recoge tareas realistas para mejorar la experiencia de desarrollo y operación sin ampliar el alcance clínico de la versión inicial.

## Desarrollo Y Operacion

- Añadir Adminer como servicio opcional en `docker-compose.override.yml` para consultar PostgreSQL por web en entorno local.
- Documentar comandos alternativos para ejecutar tests y lint dentro del contenedor `api` cuando el host no tenga dependencias Python instaladas.
- Revisar warnings de `datetime.utcnow()` y valorar migrar a fechas UTC timezone-aware.

## Documentacion

- Mantener la lista de extensiones permitidas alineada entre `ALLOWED_EXTENSIONS`, `docs/api.md` y `docs/security.md`.
- Añadir una seccion breve sobre consulta de datos operativos en PostgreSQL para administracion local.

## Fuera De Alcance Por Ahora

- No añadir autenticacion, roles, MinIO/S3 ni flujos de revision clinica sin peticion explicita.
- No modificar scripts clinicos reales sin autorizacion explicita.

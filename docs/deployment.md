# Despliegue

El despliegue inicial está pensado para un único servidor con Docker Compose.

```mermaid
flowchart TB
  Internet --> Nginx[Nginx :80]
  Nginx --> Frontend[frontend]
  Nginx --> API[api :8000]
  API --> Postgres[(postgres)]
  API --> Redis[(redis)]
  Worker[worker] --> Redis
  Worker --> Postgres
  API --> Data[(./data)]
  Worker --> Data
```

## Producción Básica

- Cambiar secretos en `.env`.
- Restringir acceso de red al servidor.
- Añadir TLS en Nginx o Caddy.
- Configurar backups de PostgreSQL y `data/`.
- Revisar política de retención antes de usar datos sensibles.

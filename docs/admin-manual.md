# Manual De Administración

## Operación Básica

```bash
make up
make logs
make down
```

## Datos

- PostgreSQL guarda metadatos, estados y auditoría.
- `data/studies/{study_id}` guarda input, output, logs y metadata.

## Backups

Respaldar PostgreSQL y `data/`. Ambos son necesarios para reconstruir trazabilidad.

## Cambio De Procesador

Actualizar `PROCESSOR_COMMAND` en `.env` y reiniciar `api` y `worker`.

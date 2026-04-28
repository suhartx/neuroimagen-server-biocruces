# Manual De Operaciones

## Comandos

- `make up`: levantar servicios.
- `make down`: parar servicios.
- `make logs`: inspeccionar logs.
- `make smoke`: comprobar healthcheck.
- `make clean`: limpiar volúmenes y estudios locales.

## Logs

- Logs de contenedores: `docker compose logs`.
- Logs técnicos del procesador: `data/studies/{study_id}/logs/processor.log`.

## Incidencias

Primero revisar estado en GUI, luego logs del worker, luego `processor.log`.

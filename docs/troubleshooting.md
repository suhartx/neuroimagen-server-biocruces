# Troubleshooting

## La GUI No Carga

Revisar `docker compose ps` y logs de `reverse-proxy` y `frontend`.

## La API No Responde

Comprobar `/api/health`, migraciones y conexión a PostgreSQL.

## El Estudio Queda En Cola

Revisar que `worker` y `redis` estén levantados.

## El Procesamiento Falla

Revisar `data/studies/{study_id}/logs/processor.log` y el valor de `PROCESSOR_COMMAND`.

## No Hay PDF

El script externo debe generar al menos un `.pdf` dentro del directorio `output`.

# Manual De Operaciones

## Comandos

- `make up`: levantar servicios.
- `make down`: parar servicios.
- `make logs`: inspeccionar logs.
- `make smoke`: comprobar healthcheck.
- `make clean`: limpiar volúmenes y estudios locales.

## Datos Y Backups

- PostgreSQL guarda metadatos, estados y auditoría.
- `data/studies/{study_id}` guarda input, BIDS, outputs, logs y metadata.
- Respaldar PostgreSQL y `data/`; ambos son necesarios para reconstruir trazabilidad.
- Hasta definir retención, los estudios y resultados se conservan indefinidamente.

Roadmap operativo recomendado para Fase 4:

- Script local de backup de PostgreSQL.
- Script local de backup de `data/studies`.
- Script de restore documentado.
- Smoke test tras restore.
- Comandos Makefile para backup, restore y verificación.
- Documentar ubicación de backups fuera de Git.

El backup útil debe tratar base de datos y filesystem como una unidad lógica. Restaurar solo PostgreSQL o solo `data/studies` puede dejar estudios sin ficheros, ficheros sin metadatos o auditoría incompleta.

## Mantenimiento

- Se usa versionado semántico: `MAJOR.MINOR.PATCH`.
- Actualizar `CHANGELOG.md` en cada release.
- Toda modificación de modelo persistente requiere migración Alembic.
- Si cambia el procesador, actualizar variables en `.env` y reiniciar `api` y `worker`.

Retención futura recomendada:

- Política inicial de 90 días para estudios no protegidos.
- Flag `keep_forever` para excluir estudios concretos.
- Modo dry-run antes de borrar físicamente.
- Auditoría de cada borrado automático o manual.
- Alerta de uso de disco en dashboard admin antes de implementar cuotas completas.

El borrado recomendado combina soft delete en base de datos con borrado físico controlado de input, BIDS, output, PNG, PDF, ZIP y logs, conservando una auditoría mínima.

## Logs

- Logs de contenedores: `docker compose logs`.
- Logs técnicos del procesador: `data/studies/{study_id}/logs/processor.log`.
- PNG renderizados: `data/studies/{study_id}/output/rendered_png/`.
- PDF técnico: `data/studies/{study_id}/output/reports/technical_report.pdf`.
- ZIP de outputs: `data/studies/{study_id}/output/outputs.zip`.
- Outputs compneuro: `data/studies/{study_id}/output/Preproc`.
- Log de renderizado: `data/studies/{study_id}/logs/rendering.log`.

## Incidencias

Primero revisar estado en GUI, luego logs del worker, luego `processor.log`. Para `compneuro`, comprobar además que existan `output/Preproc/BET`, `output/Preproc/ProbTissue`, `output/rendered_png/` y `logs/rendering.log`.

## Rerun

La reejecución no está expuesta en GUI. Si se reejecuta manualmente, conservar outputs previos en una carpeta versionada o con timestamp antes de volver a lanzar la tarea.

## Operación Futura De Jobs

- La cancelación inicial debe limitarse a jobs en cola.
- La cancelación de jobs en ejecución queda para fase posterior porque requiere gestionar procesos FSL y `compneuro` con cuidado.
- El retry de jobs fallidos debe registrar intento previo y limpiar o versionar outputs parciales.
- Los logs visibles en GUI deben truncarse y evitar rutas internas sensibles.
- El admin dashboard básico debería mostrar cola, jobs activos/fallidos, uso de disco, healthchecks, worker, Redis, PostgreSQL, usuarios y estudios por estado.

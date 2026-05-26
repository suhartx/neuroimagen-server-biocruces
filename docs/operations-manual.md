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
- PNG renderizados: `data/studies/{study_id}/output/rendered_png/`.
- PDF técnico: `data/studies/{study_id}/output/reports/technical_report.pdf`.
- ZIP de outputs: `data/studies/{study_id}/output/outputs.zip`.
- Outputs compneuro: `data/studies/{study_id}/output/Preproc`.
- Log de renderizado: `data/studies/{study_id}/logs/rendering.log`.

## Incidencias

Primero revisar estado en GUI, luego logs del worker, luego `processor.log`. Para `compneuro`, comprobar además que existan `output/Preproc/BET`, `output/Preproc/ProbTissue`, `output/rendered_png/` y `logs/rendering.log`.

## Rerun

La reejecución no está expuesta en GUI. Si se reejecuta manualmente, conservar outputs previos en una carpeta versionada o con timestamp antes de volver a lanzar la tarea.

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

En modo `dummy`, el script externo debe generar al menos un `.pdf` dentro del directorio `output`.

En modo `compneuro`, el pipeline no genera PDF clínico. La plataforma genera `output/reports/technical_report.pdf` después de detectar outputs en `output/Preproc` y renderizar PNG en `output/rendered_png/`.

## No Hay PNG Renderizados

Revisar `GENERATE_RENDERED_PNG=true`, `NIFTI_RENDERER=slicer` y `data/studies/{study_id}/logs/rendering.log`. En el worker compneuro, `slicer` debe estar disponible en el `PATH` porque proviene de FSL dentro de la imagen base.

## No Hay ZIP

Revisar que `GENERATE_OUTPUT_ZIP=true`, que el estudio esté `completed` y que existan ficheros en `data/studies/{study_id}/output/Preproc`.

## Compneuro Falla Por `/project`

`compneuro-anatproc` espera `/project/data/participants.tsv` y escribe en `/project/Preproc`. El worker crea un symlink gestionado hacia `runtime_project`. Si `/project` existe dentro del contenedor y no es un symlink gestionado, el procesamiento falla para no pisar rutas externas.

## Outputs Faltantes

El procesamiento compneuro solo se marca correcto si existen `Preproc/BET` y `Preproc/ProbTissue`. Si falta una carpeta, revisar `logs/processor.log` y permisos del volumen `./data:/app/data`.

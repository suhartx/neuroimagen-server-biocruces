# Manual De Operaciones

## Comandos

- `make up`: levantar servicios.
- `make down`: parar servicios.
- `make logs`: inspeccionar logs.
- `make smoke`: comprobar healthcheck.
- `make create-admin EMAIL=admin@example.org`: crear o actualizar el admin inicial.
- `make frontend-rebuild`: reconstruir y recrear solo el frontend Docker.
- `make rebuild`: reconstruir y recrear todos los servicios Docker.
- `make clean`: limpiar volúmenes y estudios locales.

## Usuarios

Tras aplicar migraciones, crear el primer usuario admin:

```bash
make create-admin EMAIL=admin@example.org
```

El comando pide contraseña por consola. No hay registro público abierto; los demás usuarios se crean desde la GUI con una cuenta admin.

## Datos Y Backups

- PostgreSQL guarda metadatos, estados y auditoría.
- `data/studies/{study_id}` guarda entrada, BIDS, resultados, logs y metadatos.
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

## Dashboard Admin

La GUI muestra un dashboard operativo solo para `admin` con:

- estado de cola y jobs fallidos.
- healthchecks de PostgreSQL, Redis y Worker.
- uso de disco y bytes registrados en estudios.
- usuarios y estudios por estado.
- alertas básicas que no bloquean el procesamiento.

Si Redis o Worker aparecen en `warning` o `down`, revisar `docker compose ps` y `make logs` antes de relanzar trabajos.

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
- ZIP de resultados: `data/studies/{study_id}/output/outputs.zip`.
- Outputs compneuro: `data/studies/{study_id}/output/Preproc`.
- Log de renderizado: `data/studies/{study_id}/logs/rendering.log`.

## Incidencias

Primero revisar estado en GUI, luego logs del worker, luego `processor.log`. Para `compneuro`, comprobar además que existan `output/Preproc/BET`, `output/Preproc/ProbTissue`, `output/rendered_png/` y `logs/rendering.log`.

## Retry Y Rerun

El retry de estudios fallidos está expuesto en la GUI y crea un nuevo `ProcessingJob`, conservando trazabilidad del intento anterior.

Si se reejecuta manualmente fuera de la GUI, conservar resultados previos en una carpeta versionada o con marca temporal antes de volver a lanzar la tarea.

## Operación Futura De Jobs

- La cancelación actual está limitada a jobs en cola.
- La cancelación de jobs en ejecución queda para fase posterior porque requiere gestionar procesos FSL y `compneuro` con cuidado.
- El retry de jobs fallidos crea un nuevo `ProcessingJob` y conserva trazabilidad del intento previo.
- Los logs visibles en GUI se devuelven truncados desde `processor.log` y `rendering.log`.
- El borrado aplica soft delete en DB y borrado físico de la carpeta del estudio; conserva auditoría mínima.
- El dashboard admin ya muestra cola, jobs activos/fallidos, uso de disco, healthchecks, worker, Redis, PostgreSQL, usuarios y estudios por estado.

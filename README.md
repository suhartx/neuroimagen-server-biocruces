# neuroimagen-server-biocruces

Repositorio para el TFM **"Diseño e implementación de un servicio de procesamiento de imágenes de resonancia magnética para la generación automática de informes clínicos en Neurorrehabilitación"**.

La plataforma permite subir estudios anonimizados desde una GUI web, registrar la subida, preparar una estructura BIDS por estudio, lanzar procesamiento asíncrono mediante un procesador externo tratado como componente aislado, guardar estados y descargar un PDF técnico y, cuando aplica, un ZIP de resultados.

El PDF generado en esta versión es un **informe técnico de artefactos de procesamiento**. No interpreta imágenes, no contiene conclusiones médicas y no constituye un informe clínico validado.

## Arquitectura Resumida

```mermaid
flowchart LR
  GUI[GUI React] --> API[FastAPI]
  API --> DB[(PostgreSQL)]
  API --> FS[(Filesystem data/studies)]
  API --> Redis[(Redis)]
  Redis --> Worker[Celery worker]
  Worker --> Adapter[processor_adapter]
  Adapter --> CLI[Procesador externo]
  CLI --> Outputs[Resultados del procesador]
  Worker --> Render[PNG con FSL slicer]
  Render --> Artifacts[PDF tecnico / ZIP]
  API --> Download[Descarga resultados]
  Proxy[Nginx] --> GUI
  Proxy --> API
```

## Requisitos

- Docker y Docker Compose.
- Make opcional para comandos cómodos.
- Uso inicial con datos anonimizados.

## Arranque Rápido

```bash
cp .env.example .env
make up
make create-admin EMAIL=admin@example.org
```

Abre `http://localhost` para la GUI y `http://localhost/api/docs` para Swagger/OpenAPI.

## Comandos Principales

```bash
make up       # levantar servicios
make down     # parar servicios
make logs     # ver logs
make frontend-rebuild # reconstruir/recrear solo el frontend Docker
make rebuild  # reconstruir/recrear todos los servicios Docker
make test     # ejecutar tests Python locales
make lint     # ruff check
make format   # ruff format
make migrate  # aplicar migraciones en el contenedor api
make create-admin EMAIL=admin@example.org # crear/actualizar admin inicial
make seed     # crear fichero de prueba local
make smoke    # comprobar healthcheck vía proxy
make clean    # borrar volúmenes y estudios locales
```

Cuando se modifica el frontend y se usa el despliegue Docker/Nginx, ejecuta `make frontend-rebuild` para regenerar el bundle estático y recrear el contenedor. `make down && make up` puede reutilizar una imagen anterior; `make clean` solo debe usarse si quieres borrar volúmenes y estudios locales.

## Flujo Funcional

1. El usuario inicia sesión con login local.
2. El usuario sube un fichero desde la GUI.
3. FastAPI valida permisos, extensión, sanitiza nombre y guarda el fichero en `data/studies/{study_id}/input`.
4. Se crea un `Study` con propietario, un `ProcessingJob` y eventos de auditoría.
5. FastAPI encola una tarea Celery en Redis.
6. El worker ejecuta `processor_adapter`.
7. El adaptador ejecuta el comando correspondiente al backend configurado.
8. En modo `dummy`, se usa `PROCESSOR_COMMAND`; en modo `compneuro`, se usa `COMPNEURO_COMMAND`.
9. El procesador dummy genera un PDF de desarrollo o `compneuro-anatproc` genera `Preproc/BET` y `Preproc/ProbTissue`.
10. El worker detecta resultados, renderiza NIfTI a PNG con FSL `slicer`, genera un PDF técnico y opcionalmente un ZIP.
11. La GUI permite ver detalle/logs, cancelar jobs en cola, reintentar fallidos, borrar estudios permitidos y descargar PDF/ZIP si el usuario tiene permiso.

## Procesadores

El backend de procesamiento se selecciona con `PROCESSOR_BACKEND`.

| Backend | Uso | Comando ejecutado |
| --- | --- | --- |
| `dummy` | Desarrollo y pruebas rápidas sin flujo real. | `PROCESSOR_COMMAND` |
| `compneuro` | Integración real con `compneuro-anatproc` para T1w `.nii.gz`. | `COMPNEURO_COMMAND` |

`PROCESSOR_COMMAND` es una plantilla para el procesador de desarrollo. Permite cambiar el script dummy sin tocar FastAPI ni Celery:

```env
PROCESSOR_COMMAND=python /app/external_processor/dummy_processor.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

Placeholders disponibles: `{input_dir}`, `{output_dir}`, `{study_id}`, `{logs_dir}`.

Para `compneuro`, el worker debe construirse con `WORKER_DOCKERFILE=worker/Dockerfile.compneuro` y `PROCESSOR_BACKEND=compneuro`. En este modo el comando relevante es:

```env
COMPNEURO_COMMAND=bash /app/src/apreproc_launcher.sh
```

No se usa Docker-in-Docker: Celery corre dentro de una imagen derivada de `compneurobilbaolab/compneuro-anatproc:1.1`, ejecuta `src/apreproc_launcher.sh` y después usa FSL `slicer` para crear PNG técnicos desde los NIfTI generados.

## Estructura

```text
backend/              API FastAPI, modelos, migraciones
frontend/             GUI React/Vite
worker/               tareas Celery
processor_adapter/    adaptador CLI desacoplado
external_processor/   procesador dummy de desarrollo
infra/reverse-proxy/  Nginx
docs/                 documentación TFM y operación
scripts/              scripts de operación y validación
tests/                tests básicos
data/studies/         almacenamiento local ignorado por Git
```

Cada carpeta de primer nivel incluye su propio `README.md` explicando para qué sirve y cómo está organizado su código o contenido.

## Limitaciones Iniciales

- Sin anonimización DICOM integrada.
- Sin revisión clínica formal.
- Sin retención automática de datos.
- Sin compartición de informes mediante enlaces firmados.
- Sin notificaciones por email.
- Sin subida múltiple ni lotes.
- Sin MinIO/S3 en esta versión.
- El procesador dummy no tiene validez clínica.
- La integración `compneuro-anatproc` inicial ejecuta solo `src/apreproc_launcher.sh`; `brainmeasures.sh` queda como mejora futura.
- El PDF de la integración real es un resumen técnico de procesamiento con PNG renderizados desde resultados NIfTI; no es un informe clínico.

## Roadmap

El roadmap detallado está en `docs/roadmap.md` y organiza la evolución por fases. La **Fase 3 — Admin dashboard** ya añade visibilidad operativa para administradores: estado de cola, jobs activos/fallidos, uso de disco, healthchecks, usuarios y estudios por estado. La siguiente fase recomendada es **Fase 4 — Backups y mantenimiento**.

Quedan para fases posteriores: Google/OIDC, ORCID, compartición mediante enlaces firmados, notificaciones, múltiples subidas, retención automática, cuotas, flujos de procesamiento configurables e integración institucional.

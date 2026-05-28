# Arquitectura

El sistema usa una arquitectura desacoplada para evitar que la API web dependa del algoritmo clínico. El procesador externo se invoca mediante `processor_adapter` como caja negra y puede seleccionarse por configuración (`dummy` o `compneuro`).

```mermaid
flowchart TB
  subgraph Client
    Browser[GUI web castellano]
  end
  subgraph DockerHost[Servidor unico Docker Compose]
    Proxy[Nginx reverse-proxy]
    Frontend[frontend React]
    API[api FastAPI]
    DB[(PostgreSQL)]
    Redis[(Redis broker)]
    Worker[Celery worker]
    Adapter[processor_adapter]
    Script[procesador externo]
    Render[Render NIfTI a PNG con FSL slicer]
    Artifacts[PDF tecnico / ZIP]
    Storage[(data/studies filesystem)]
  end
  Browser --> Proxy
  Proxy --> Frontend
  Proxy --> API
  API --> DB
  API --> Storage
  API --> Redis
  Redis --> Worker
  Worker --> DB
  Worker --> Storage
  Worker --> Adapter
  Adapter --> Script
  Script --> Storage
  Worker --> Render
  Render --> Artifacts
  Artifacts --> Storage
```

Para `compneuro-anatproc`, el servicio `worker` puede construirse con `worker/Dockerfile.compneuro`, derivado de `compneurobilbaolab/compneuro-anatproc:1.1`. No se usa Docker-in-Docker: Celery, el launcher externo y FSL `slicer` conviven en el mismo contenedor worker.

No existe un contenedor `compneuro-anatproc` anidado dentro del `worker`. El `worker` es una imagen derivada de `compneurobilbaolab/compneuro-anatproc:1.1`; por eso ejecuta directamente los scripts y herramientas de neuroimagen dentro del mismo contenedor.

## Componentes

- `frontend`: interfaz simple para subida, listado, estado y descarga.
- `api`: valida entradas, registra estudios, prepara BIDS, expone OpenAPI y descarga PDFs/ZIPs.
- `worker`: ejecuta tareas largas fuera del ciclo HTTP.
- `processor_adapter`: contrato estable con el procesador externo y estrategia por backend.
- `postgres`: persistencia relacional.
- `redis`: cola de tareas.
- `filesystem`: almacenamiento inicial sustituible por S3/MinIO futuro.
- `reverse-proxy`: punto de entrada HTTP.

## Modelo ER

```mermaid
erDiagram
  Study ||--o{ ProcessingJob : has
  Study ||--o{ AuditEvent : emits
  Study {
    uuid id PK
    string original_filename
    text stored_path
    text output_path
    text pdf_path
    text output_zip_path
    string bids_subject_id
    string processor_backend
    string container_image
    text bids_path
    text preproc_output_path
    text rendered_png_dir
    text processing_warnings
    enum status
    datetime created_at
    datetime updated_at
    datetime processing_started_at
    datetime processing_finished_at
    text error_message
    string processor_name
    string processor_version
    bigint file_size
    string checksum
  }
  ProcessingJob {
    uuid id PK
    uuid study_id FK
    string status
    datetime queued_at
    datetime started_at
    datetime finished_at
    int retry_count
    string worker_name
    int exit_code
    text log_path
    text error_message
  }
  AuditEvent {
    uuid id PK
    uuid study_id FK
    string event_type
    datetime timestamp
    text details
    string actor
    string ip_address
  }
```

## Estados

```mermaid
stateDiagram-v2
  [*] --> uploaded
  uploaded --> queued
  queued --> processing
  processing --> completed
  processing --> failed
  completed --> [*]
  failed --> [*]
```

Estados futuros documentados: `review_pending`, `reviewed`, `rejected`, `archived`.

No se añade un estado `bids_prepared` en la primera integración: la preparación BIDS ocurre antes de encolar y queda trazada mediante campos y auditoría. Si falla, la subida responde con error y no crea un estudio procesable.

## Worker Compneuro

```mermaid
flowchart LR
  API[FastAPI] --> Data[(data/studies)]
  API --> Redis[(Redis)]
  Redis --> Worker[Celery worker compneuro]
  Worker --> Adapter[CompneuroAnatprocAdapter]
  Adapter --> Project[/project symlink gestionado]
  Project --> BIDS[bids_project/data]
  Project --> Preproc[output/Preproc]
  Adapter --> Launcher[src/apreproc_launcher.sh]
  Launcher --> Preproc
  Worker --> PNG[output/rendered_png]
  PNG --> PDF[output/reports/technical_report.pdf]
  Worker --> ZIP[output/outputs.zip]
```

No se mantiene una copia local de `compneuro-anatproc/` como dependencia del proyecto. El worker real parte de la imagen Docker publicada y, durante el build, copia únicamente los scripts versionados necesarios para ejecutar `src/apreproc_launcher.sh`.

## Decisiones Arquitectónicas

- La API no ejecuta procesamiento de neuroimagen; valida, prepara datos, registra el estudio y encola la tarea.
- Celery ejecuta el procesamiento largo fuera del ciclo HTTP para evitar bloqueos y permitir trazabilidad de estados.
- `processor_adapter` mantiene al procesador externo como caja negra y evita acoplar FastAPI al pipeline clínico.
- El post-procesado técnico se ejecuta en el mismo worker porque FSL ya está disponible y se evitan contenedores, volúmenes y sincronización adicionales.
- El PDF generado es técnico y no contiene interpretación clínica ni conclusiones médicas.

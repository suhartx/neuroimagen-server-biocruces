# Arquitectura

El sistema usa una arquitectura desacoplada para evitar que la API web dependa del algoritmo clínico. El script externo se invoca mediante `processor_adapter` como caja negra.

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
    Script[script Python externo]
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
```

## Componentes

- `frontend`: interfaz simple para subida, listado, estado y descarga.
- `api`: valida entradas, registra estudios, expone OpenAPI y descarga PDFs.
- `worker`: ejecuta tareas largas fuera del ciclo HTTP.
- `processor_adapter`: contrato estable con el script CLI externo.
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

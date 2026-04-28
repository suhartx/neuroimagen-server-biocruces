# Pipeline De Procesamiento

El procesamiento tarda entre minutos y una hora, por eso nunca se ejecuta en la petición HTTP.

```mermaid
sequenceDiagram
  participant U as Usuario
  participant F as Frontend
  participant A as FastAPI
  participant D as PostgreSQL
  participant R as Redis
  participant W as Celery Worker
  participant P as Processor Adapter
  participant S as Script externo
  participant FS as Filesystem
  U->>F: Selecciona fichero
  F->>A: POST /api/studies/upload
  A->>FS: Guarda input
  A->>D: Crea Study y ProcessingJob
  A->>R: Encola tarea
  A-->>F: 201 queued
  R->>W: Entrega tarea
  W->>D: processing
  W->>P: run(input, output, study_id, logs)
  P->>S: Ejecuta CLI configurada
  S->>FS: Genera PDF
  P-->>W: Resultado y ruta PDF
  W->>D: completed o failed
  F->>A: Consulta estudios
  F->>A: Descarga PDF
```

## Contrato Del Adaptador

Entrada:

- `input_dir`
- `output_dir`
- `study_id`
- `logs_dir`
- `PROCESSOR_COMMAND`

Salida:

- éxito/error.
- código de salida.
- ruta del PDF.
- log técnico.
- mensaje de error.
- duración.

El comando se configura con placeholders:

```env
PROCESSOR_COMMAND=python /app/external_processor/process.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

El adaptador valida entrada, crea salida, captura stdout/stderr, guarda logs, detecta errores y comprueba que se genere al menos un PDF.

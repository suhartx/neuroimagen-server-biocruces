# Pipeline De Procesamiento

El procesamiento tarda entre minutos y una hora, por eso nunca se ejecuta en la petición HTTP. La API prepara datos y encola; el worker ejecuta el procesador configurado.

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
  U->>F: Selecciona T1w .nii.gz y sujeto BIDS
  F->>A: POST /api/studies/upload
  A->>FS: Guarda input/original
  A->>FS: Prepara bids_project/data
  A->>D: Crea Study y ProcessingJob
  A->>R: Encola tarea
  A-->>F: 201 queued
  R->>W: Entrega tarea
  W->>D: processing
  W->>P: run(input, output, study_id, logs, bids_project)
  P->>S: Ejecuta backend configurado
  S->>FS: Genera PDF dummy o Preproc
  P-->>W: Resultado y outputs detectados
  W->>FS: Renderiza NIfTI con FSL slicer
  W->>FS: Genera PDF tecnico y ZIP si aplica
  W->>D: completed o failed
  F->>A: Consulta estudios
  F->>A: Descarga PDF tecnico / ZIP
```

## Contrato Del Adaptador

Entrada:

- `input_dir`
- `output_dir`
- `study_id`
- `logs_dir`
- backend configurado (`PROCESSOR_BACKEND`)

Salida:

- éxito/error.
- código de salida.
- ruta del PDF, si el backend lo genera o si la plataforma crea un PDF técnico.
- rutas de PNG renderizados desde NIfTI, si aplica.
- lista de outputs.
- ruta del ZIP, si aplica.
- log técnico.
- mensaje de error.
- duración.

El adaptador elige el comando según `PROCESSOR_BACKEND`. El backend `dummy` ejecuta `PROCESSOR_COMMAND` con placeholders:

```env
PROCESSOR_COMMAND=python /app/external_processor/process.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

El adaptador valida entrada, crea salida, captura stdout/stderr y guarda logs. En `dummy` comprueba que se genere al menos un PDF. En `compneuro` ejecuta `COMPNEURO_COMMAND`, por defecto `bash /app/src/apreproc_launcher.sh`, comprueba exit code `0` y valida que existan `Preproc/BET` y `Preproc/ProbTissue`.

## BIDS Por Estudio

```text
data/studies/{study_id}/
  input/original/{fichero_original}.nii.gz
  bids_project/data/sub-XXXX/anat/sub-XXXX_T1w.nii.gz
  bids_project/data/participants.tsv
  bids_project/data/dataset_description.json
  runtime_project/data -> ../bids_project/data
  runtime_project/Preproc -> ../output/Preproc
  output/Preproc/BET
  output/Preproc/ProbTissue
  output/rendered_png
  output/reports/technical_report.pdf
  output/outputs.zip
  logs/processor.log
  logs/rendering.log
```

`compneuro-anatproc` usa rutas hardcodeadas bajo `/project`. La plataforma crea un `runtime_project` aislado por estudio y el worker compneuro apunta `/project` a esa carpeta mediante symlink gestionado. Esto evita Docker-in-Docker y evita modificar los scripts externos.

## Flujo Compneuro

```mermaid
flowchart TD
  Upload[Subida .nii.gz] --> Validate[Validar extension y sub-XXXX]
  Validate --> BIDS[Preparar BIDS]
  BIDS --> Queue[Encolar Celery]
  Queue --> Worker[Worker compneuro]
  Worker --> Mount[Preparar /project]
  Mount --> Launcher[src/apreproc_launcher.sh]
  Launcher --> BET[Preproc/BET]
  Launcher --> Prob[Preproc/ProbTissue]
  BET --> Render[PNG con FSL slicer]
  Prob --> Render
  Render --> Report[PDF tecnico]
  BET --> Zip[outputs.zip]
  Prob --> Zip
```

## Post-Procesado Técnico

Después de una ejecución correcta de `compneuro`, el worker busca `.nii` y `.nii.gz` dentro de `output/Preproc`, con límite configurable por `NIFTI_RENDER_MAX_FILES`. Cada fichero se renderiza con FSL `slicer` usando el patrón conceptual `slicer input.nii.gz -a output.png` y se guarda en `output/rendered_png/`.

El PDF se guarda por defecto en `output/reports/technical_report.pdf` e incluye metadatos del estudio, sujeto BIDS, pipeline usado, listado de outputs, nombre de cada NIfTI y la imagen PNG renderizada. Si no hay NIfTI o falla alguna conversión, el PDF se genera igual con avisos técnicos. Estos avisos no son trazas internas y pueden mostrarse en la GUI.

El documento es un informe técnico de artefactos generados. No interpreta imágenes ni constituye un informe clínico validado.

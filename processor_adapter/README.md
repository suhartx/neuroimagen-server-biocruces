# Processor Adapter

Esta carpeta contiene la frontera obligatoria entre la plataforma web y el script externo de procesamiento de neuroimagen.

## Responsabilidad

- Tratar el script externo como componente aislado.
- Recibir rutas de entrada, salida, logs e identificador de estudio.
- Seleccionar backend por `PROCESSOR_BACKEND`.
- Construir el comando CLI desde `PROCESSOR_COMMAND` en modo `dummy` o `COMPNEURO_COMMAND` en modo `compneuro`.
- Ejecutar el comando y capturar `stdout`/`stderr`.
- Guardar logs técnicos.
- Detectar resultados generados por el backend configurado.
- Renderizar NIfTI a PNG y generar artefactos técnicos cuando lo pide el worker.
- Devolver un resultado estructurado al worker.

## Estructura Del Código

- `adapter.py`: define `ProcessorAdapter` y `ProcessorResult`.
- `nifti_renderer.py`: busca `.nii`/`.nii.gz` en `Preproc` y ejecuta FSL `slicer`.
- `technical_pdf_report.py`: genera el PDF técnico con metadatos e imágenes PNG.
- `output_packager.py`: genera ZIP de resultados con rutas relativas.
- `artifacts.py`: mantiene compatibilidad con imports previos.
- `__init__.py`: exporta las clases públicas del paquete.

## `ProcessorResult`

El resultado contiene:

- `success`: indica si la ejecución del backend fue correcta.
- `exit_code`: código de salida del proceso externo.
- `pdf_path`: ruta del primer PDF detectado o del PDF técnico generado por la plataforma.
- `log_path`: ruta del fichero de log generado.
- `error_message`: mensaje controlado para diagnóstico.
- `duration_seconds`: duración total.
- `output_files`: resultados detectados.
- `output_zip_path`: ZIP generado por la plataforma, si aplica.
- `preproc_path`: ruta `output/Preproc` en modo `compneuro`.
- `warnings`: avisos técnicos no bloqueantes.

## Seguridad Y Acoplamiento

El adaptador valida que exista el directorio de entrada y crea salida/logs si faltan. No interpreta el contenido médico ni modifica el procesador externo.

Ejemplo de comando:

```env
PROCESSOR_COMMAND=python /app/external_processor/dummy_processor.py --input {input_dir} --output {output_dir} --study-id {study_id}
```

Para `compneuro`, el comando por defecto es:

```env
COMPNEURO_COMMAND=bash /app/src/apreproc_launcher.sh
```

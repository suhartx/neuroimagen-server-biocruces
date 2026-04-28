# Procesador Dummy De Desarrollo

Este directorio contiene `dummy_processor.py`, una herramienta de desarrollo para probar el flujo completo sin disponer todavía del script clínico real.

No implementa procesamiento clínico, no analiza imágenes y no debe usarse para decisiones médicas.

Contrato compatible:

```bash
python external_processor/dummy_processor.py --input data/studies/<id>/input --output data/studies/<id>/output --study-id <id>
```

Para sustituirlo por el script real, configurá `PROCESSOR_COMMAND` en `.env` manteniendo los placeholders `{input_dir}`, `{output_dir}`, `{study_id}` y opcionalmente `{logs_dir}`.

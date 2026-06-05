# External Processor

Esta carpeta representa el lugar donde vive, o desde donde se monta, el procesador externo de neuroimagen.

## Responsabilidad

- Alojar el procesador dummy de desarrollo.
- Documentar cómo conectar un procesador externo sin acoplarlo al backend.
- Mantener claro que el algoritmo de procesamiento no forma parte de esta plataforma inicial.

## Código Incluido

- `dummy_processor.py`: herramienta de desarrollo para probar el flujo completo sin disponer todavía del procesador externo real.
- `README.md`: esta explicación.

## `dummy_processor.py`

El script dummy recibe `--input`, `--output` y `--study-id`. Espera unos segundos y escribe un PDF mínimo válido en el directorio de salida.

No implementa análisis de imagen, no interpreta resultados y no debe usarse para decisiones médicas.

Contrato compatible:

```bash
python external_processor/dummy_processor.py --input data/studies/<id>/input --output data/studies/<id>/output --study-id <id>
```

Para sustituirlo por el script real, configura `PROCESSOR_COMMAND` en `.env` manteniendo los placeholders `{input_dir}`, `{output_dir}`, `{study_id}` y opcionalmente `{logs_dir}`.

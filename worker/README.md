# Worker

Esta carpeta contiene el proceso asíncrono Celery. Su trabajo es ejecutar procesamiento largo fuera del ciclo petición-respuesta HTTP.

## Responsabilidad

- Consumir tareas desde Redis.
- Cambiar estados de `Study` y `ProcessingJob`.
- Invocar `processor_adapter`.
- Renderizar resultados NIfTI a PNG con FSL `slicer` cuando el backend es `compneuro`.
- Guardar ruta de PDF, ZIP, PNG y logs técnicos.
- Marcar fallos de forma controlada.

## Estructura Del Código

- `celery_app.py`: crea la aplicación Celery usando `CELERY_BROKER_URL` y `CELERY_RESULT_BACKEND`.
- `tasks.py`: define la tarea `process_study`.
- `__init__.py`: marca el directorio como paquete Python.

## Flujo De La Tarea `process_study`

1. Recibe `study_id` y `job_id`.
2. Recupera registros desde PostgreSQL.
3. Marca el estudio como `processing`.
4. Construye rutas `input`, `output` y `logs` con `LocalStudyStorage`.
5. Ejecuta `ProcessorAdapter.run(...)`.
6. Para `compneuro`, busca NIfTI en `output/Preproc`, genera PNG, PDF técnico y ZIP si están habilitados.
7. Si hay PDF, marca `completed` y guarda `pdf_path`.
8. Si falla, marca `failed` y guarda un mensaje técnico resumido.
9. Registra eventos de auditoría.

## Límite Crítico

El worker no debe implementar análisis de imagen ni interpretación médica. Solo coordina ejecución, estados, logs y persistencia. El procesador externo entra por `processor_adapter`.

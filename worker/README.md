# Worker

Esta carpeta contiene el proceso asíncrono Celery. Su trabajo es ejecutar procesamiento largo fuera del ciclo petición-respuesta HTTP.

## Responsabilidad

- Consumir tareas desde Redis.
- Cambiar estados de `Study` y `ProcessingJob`.
- Invocar `processor_adapter`.
- Guardar ruta de PDF y logs técnicos.
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
6. Si hay PDF, marca `completed` y guarda `pdf_path`.
7. Si falla, marca `failed` y guarda un mensaje técnico resumido.
8. Registra eventos de auditoría.

## Límite Crítico

El worker no debe implementar lógica clínica. Solo coordina ejecución, estados, logs y persistencia. La caja negra clínica entra por `processor_adapter`.

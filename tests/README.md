# Tests

Esta carpeta contiene pruebas automatizadas básicas. No busca cubrir todo el sistema, sino validar los puntos de mayor riesgo de la primera versión.

## Responsabilidad

- Verificar que la API responde.
- Verificar que se puede crear un estudio mediante subida.
- Verificar que se rechazan extensiones no permitidas.
- Verificar que el adaptador detecta PDFs generados.
- Verificar que el adaptador informa fallos del script externo.
- Verificar que el worker marca `failed` si el procesador falla.

## Estructura Del Código

- `conftest.py`: configura fixtures de pytest, base SQLite temporal y cliente FastAPI.
- `test_api.py`: prueba healthcheck, subida y validación de extensión.
- `test_processor_adapter.py`: prueba el contrato del adaptador con el dummy y escenarios de error.
- `test_worker.py`: prueba transición a fallo en el worker cuando el comando externo falla.

## Ejecución

```bash
make test
```

Si se ejecuta fuera de contenedor, instalá antes las dependencias de `backend/requirements.txt`.

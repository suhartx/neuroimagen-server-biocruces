# Tests

Esta carpeta contiene pruebas automatizadas básicas. No busca cubrir todo el sistema, sino validar los puntos de mayor riesgo: permisos, subida, cola, adapter, worker y artefactos técnicos.

## Responsabilidad

- Verificar autenticación local, roles y permisos por propietario.
- Verificar subida, validación de extensiones y BIDS básico.
- Verificar detalle de jobs, logs truncados, cancelación de jobs en cola, retry y borrado.
- Verificar dashboard admin y bloqueo para `researcher`.
- Verificar adapter dummy/compneuro simulado y errores controlados.
- Verificar renderizado/artefactos técnicos sin ejecutar FSL real.
- Verificar que el worker marca `failed` si el procesador falla.

## Estructura Del Código

- `conftest.py`: configura fixtures de pytest, base SQLite temporal y cliente FastAPI.
- `test_api.py`: prueba auth, permisos, estudios, jobs, dashboard, descargas y acciones.
- `test_bids.py`: prueba preparación BIDS y sujeto seguro.
- `test_processor_adapter.py`: prueba el contrato del adaptador con el dummy y escenarios de error.
- `test_worker.py`: prueba transiciones principales del worker ante éxito/error simulado.

## Ejecución

```bash
make test
```

Si se ejecuta fuera de contenedor, instalá antes las dependencias de `backend/requirements.txt`.

# Tests

Esta carpeta contiene pruebas automatizadas básicas. No busca cubrir todo el sistema, sino validar los puntos de mayor riesgo: permisos, subida, cola, adapter, worker y artefactos técnicos.

## Responsabilidad

- Verificar autenticación local, roles y permisos por propietario.
- Verificar subida, validación de extensiones y BIDS básico.
- Verificar detalle de jobs, logs truncados, cancelación de jobs en cola o en procesamiento, retry y borrado.
- Verificar dashboard admin y bloqueo para `researcher`.
- Verificar cuotas por usuario, enlaces compartidos, notificaciones y revisión técnica.
- Verificar adapter dummy/compneuro simulado y errores controlados.
- Verificar renderizado/artefactos técnicos sin ejecutar FSL real.
- Verificar que el worker marca `failed` si el procesador falla y `canceled` si el procesamiento se interrumpe.

## Estructura Del Código

- `conftest.py`: configura fixtures de pytest, base SQLite temporal y cliente FastAPI.
- `test_api.py`: prueba auth, permisos, estudios, jobs, dashboard, descargas, cuotas, sharing, notificaciones, revisión técnica y acciones.
- `test_bids.py`: prueba preparación BIDS y sujeto seguro.
- `test_processor_adapter.py`: prueba la interfaz esperada del adaptador con el dummy y escenarios de error.
- `test_worker.py`: prueba transiciones principales del worker ante éxito, error y cancelación simulada.
- `test_notifications.py`: prueba detalles de envío SMTP, incluyendo STARTTLS antes de autenticación.

## Ejecución

```bash
make test
```

Si se ejecuta fuera de contenedor, instalá antes las dependencias de `backend/requirements.txt`.

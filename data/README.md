# Data

Esta carpeta es el punto de montaje local para datos generados por la aplicación.

## Responsabilidad

- Guardar estudios subidos.
- Guardar resultados PDF.
- Guardar logs técnicos del procesador.
- Mantener metadatos locales por estudio.

## Estructura Esperada

```text
data/
  studies/
    {study_id}/
      input/
      output/
      logs/
      metadata.json
```

## Qué Se Versiona

Solo se versionan `.gitkeep` y este `README.md`. Los estudios reales, resultados y logs están ignorados por Git.

## Advertencia

No guardar datos clínicos identificativos. La versión inicial asume estudios anonimizados y no implementa política de retención.

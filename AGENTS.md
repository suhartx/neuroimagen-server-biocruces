# AGENTS.md

## Contexto

Repositorio TFM para integración de procesamiento asíncrono de neuroimagen. El valor arquitectónico está en la plataforma, la trazabilidad y el adaptador, no en reimplementar el algoritmo clínico.

## Reglas

- Leer `README.md`, `docs/architecture.md` y `docs/processing-pipeline.md` antes de cambios.
- No modificar scripts clínicos reales sin autorización explícita.
- Usar `processor_adapter` como frontera obligatoria.
- No añadir autenticación, roles, MinIO ni funcionalidades futuras salvo petición explícita.
- Mantener GUI simple y en castellano.
- No usar datos clínicos reales.
- No introducir secretos.
- Actualizar tests y docs junto con cambios funcionales.
- Usar Conventional Commits.

## Checks Recomendados

```bash
make test
make lint
make check-docs
make check-secrets
```

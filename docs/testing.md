# Testing

Tests actuales:

- healthcheck API.
- creación de estudio mediante subida.
- validación de extensión.
- adapter con procesador dummy.
- detección de PDF generado.
- fallo de script externo.
- salida sin PDF.

Ejecutar:

```bash
make test
```

Lint Python:

```bash
make lint
```

Validación frontend:

```bash
cd frontend
npm install
npm run lint
```

El lint frontend usa `frontend/eslint.config.js`, compatible con ESLint 9. `package-lock.json` debe mantenerse actualizado cuando cambien dependencias frontend.

No se ejecuta build automáticamente por decisión del proyecto.

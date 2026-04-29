# Instalación

1. Clonar o abrir el repositorio.
2. Crear configuración local:

```bash
cp .env.example .env
```

3. Revisar contraseñas, rutas y `PROCESSOR_COMMAND` según `docs/configuration.md`.
4. Levantar servicios:

```bash
make up
```

5. Acceder a:

- GUI: `http://localhost`
- Swagger: `http://localhost/api/docs`

No uses datos clínicos reales en esta versión inicial.

# Scripts

Esta carpeta contiene scripts pequeños de operación y validación.

## Responsabilidad

- Facilitar comandos repetitivos usados por `Makefile`.
- Evitar instrucciones manuales propensas a error.
- Preparar checks básicos para desarrollo y pre-commit.

## Scripts

- `start.sh`: levanta servicios con `docker compose up -d`.
- `stop.sh`: detiene servicios con `docker compose down`.
- `smoke.sh`: comprueba el healthcheck vía reverse proxy.
- `check-docs.sh`: valida que exista la documentación mínima obligatoria.
- `check-no-secrets.sh`: busca señales simples de secretos o `.env` commiteados.
- `seed.sh`: crea un fichero dummy local para pruebas manuales.

## Relación Con Makefile

El `Makefile` llama a estos scripts mediante comandos como `make smoke`, `make check-docs`, `make check-secrets` y `make seed`.

## Criterio

Los scripts deben seguir siendo simples, legibles y seguros. No deben borrar datos reales salvo que el comando lo indique claramente.

# Infra

Esta carpeta contiene configuración de infraestructura local del proyecto.

## Responsabilidad

- Configurar el reverse proxy.
- Separar infraestructura de código de aplicación.
- Documentar decisiones de despliegue reproducible con Docker Compose.

## Estructura Del Código

- `reverse-proxy/nginx.conf`: configuración de Nginx usada por el servicio `reverse-proxy`.

## Flujo Del Proxy

- Las rutas `/api/` se envían al servicio `api:8000`.
- El resto de rutas se envían al servicio `frontend:80`.
- `client_max_body_size` permite subidas grandes configuradas para estudios de neuroimagen.

## Futuro

En una fase hospitalaria habría que añadir TLS real, cabeceras de seguridad, límites más finos, logs de acceso controlados y hardening.

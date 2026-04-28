# Frontend

Esta carpeta contiene la GUI web sencilla en castellano. Está implementada con React y Vite, y se sirve como sitio estático detrás del reverse proxy.

## Responsabilidad

- Mostrar una pantalla clara para subir estudios anonimizados.
- Listar estudios registrados.
- Mostrar estados de procesamiento.
- Permitir descargar el PDF cuando esté disponible.
- Mostrar advertencias de uso clínico responsable.

## Estructura Del Código

- `src/main.jsx`: contiene la aplicación React principal. Gestiona estado local, subida del fichero, consulta periódica de estudios y enlaces de descarga.
- `src/styles.css`: define el estilo visual de la interfaz.
- `index.html`: punto de entrada HTML de Vite.
- `package.json`: scripts y dependencias frontend.
- `Dockerfile`: compila el frontend y lo sirve con Nginx.
- `nginx.conf`: configuración mínima para servir la SPA.

## Flujo En La UI

1. El usuario selecciona un fichero.
2. La UI envía `POST /api/studies/upload` con `FormData`.
3. La UI refresca el listado de estudios.
4. Cada 5 segundos consulta `/api/studies` para actualizar estados.
5. Si `has_pdf` es verdadero, muestra el enlace de descarga.

## Criterio De Diseño

La interfaz es deliberadamente simple. No incluye login, roles, revisión clínica ni flujos hospitalarios futuros porque no forman parte de esta versión inicial.

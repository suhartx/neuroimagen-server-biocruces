# Frontend

Esta carpeta contiene la GUI web sencilla en castellano. Está implementada con React y Vite, y se sirve como sitio estático detrás del reverse proxy.

## Responsabilidad

- Mostrar login local y mantener sesión JWT en cliente.
- Mostrar una pantalla clara para subir estudios anonimizados.
- Listar estudios visibles según permisos.
- Mostrar estados de procesamiento.
- Permitir descargar PDF/ZIP cuando estén disponibles y el usuario tenga permiso.
- Permitir gestión básica de usuarios para admin.
- Mostrar advertencias de uso clínico responsable.

## Estructura Del Código

- `src/main.jsx`: contiene la aplicación React principal. Gestiona login, token, subida del fichero, consulta periódica de estudios, descarga autenticada y usuarios admin.
- `src/styles.css`: define el estilo visual de la interfaz.
- `index.html`: punto de entrada HTML de Vite.
- `package.json`: scripts y dependencias frontend.
- `package-lock.json`: versiones resueltas de dependencias frontend para instalaciones reproducibles.
- `eslint.config.js`: configuración de lint compatible con ESLint 9.
- `Dockerfile`: compila el frontend y lo sirve con Nginx.
- `nginx.conf`: configuración mínima para servir la SPA.

## Desarrollo Y Validación

```bash
npm install
npm run lint
```

`src/main.jsx` concentra los componentes actuales de la GUI (`App` y `Status`). Si la interfaz crece, separar componentes solo cuando mejore claramente la legibilidad o reutilización.

## Flujo En La UI

1. El usuario inicia sesión contra `/api/auth/login`.
2. La UI guarda el token local y consulta `/api/auth/me`.
3. El usuario selecciona un fichero.
4. La UI envía `POST /api/studies/upload` con `FormData` y `Authorization: Bearer`.
5. La UI refresca el listado de estudios permitido para el usuario.
6. Cada 5 segundos consulta `/api/studies` para actualizar estados.
7. Si `has_pdf` o `has_output_zip` es verdadero, descarga con `fetch` autenticado.

## Criterio De Diseño

La interfaz es deliberadamente simple. Incluye login local, historial por usuario y creación básica de usuarios admin. No incluye sharing, notificaciones, revisión clínica ni flujos hospitalarios futuros.

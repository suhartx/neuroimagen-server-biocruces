# Manual De Desarrollo

## Entorno Local

```bash
cp .env.example .env
make up
make test
```

El significado de cada variable de `.env` está documentado en `docs/configuration.md`.

## Backend

- FastAPI en `backend/app`.
- Modelos en `backend/app/models`.
- Migraciones Alembic en `backend/alembic`.

## Worker

- Celery en `worker/`.
- No añadir lógica clínica al worker; usar `processor_adapter`.
- `worker/Dockerfile.compneuro` construye el worker real sobre la imagen de `compneuro-anatproc` y añade dependencias de la plataforma.
- El post-procesado técnico corre en el mismo worker: renderiza NIfTI con FSL `slicer`, genera PDF y empaqueta outputs.
- La concurrencia recomendada para `compneuro` es `1`, porque el pipeline usa `/project` como ruta fija.

## Processor Adapter

- `processor_adapter.adapter.DummyProcessorAdapter`: mantiene el procesador de desarrollo con PDF.
- `processor_adapter.adapter.CompneuroAnatprocAdapter`: prepara `/project`, ejecuta `src/apreproc_launcher.sh` y valida `Preproc/BET` y `Preproc/ProbTissue`.
- `processor_adapter.nifti_renderer`: encuentra `.nii`/`.nii.gz` en `Preproc` y ejecuta `slicer input -a output.png`.
- `processor_adapter.technical_pdf_report`: genera el PDF técnico con metadatos, listado de outputs y PNG renderizados.
- `processor_adapter.output_packager`: genera el ZIP de outputs con rutas relativas.
- `processor_adapter.artifacts`: puente de compatibilidad para imports existentes.

## BIDS

- `backend/app/services/bids.py` prepara BIDS para un único T1w por estudio.
- No se usan sesiones BIDS en esta fase.
- `bids_subject_id` debe tener formato `sub-XXXX`; ejemplo: `sub-O01`.

## Frontend

- React/Vite en `frontend/`.
- UI sencilla, castellano, clara y sin flujos clínicos no implementados.
- Instalar dependencias con `npm install` desde `frontend/`; el `package-lock.json` fija las versiones resueltas para reproducibilidad.
- Validar cambios frontend con `npm run lint`; la configuración vive en `frontend/eslint.config.js` y usa el formato flat config de ESLint 9.

## Convenciones

- Conventional Commits.
- Actualizar tests ante cambios funcionales.
- Actualizar docs si cambia arquitectura, API, despliegue o pipeline.
- Documentar cambios de tooling frontend cuando afecten instalación, lint o estructura de componentes.

## Próxima Fase Recomendada: Multiusuario Básico

La siguiente implementación funcional debería introducir login local, roles `admin`/`researcher`, propietario por estudio e historial por usuario. No conviene empezar por Google, ORCID, sharing, email, cuotas o pipelines configurables avanzados porque todos dependen de identidad y permisos.

Orden técnico sugerido:

1. Crear modelo `User` y migración Alembic.
2. Definir creación del primer admin.
3. Implementar hashing de contraseña y login local.
4. Implementar sesión o JWT con expiración y documentar la elección.
5. Añadir `owner_user_id` a `Study` y migrar estudios existentes a usuario `system` o admin.
6. Proteger endpoints y aplicar filtros por propietario.
7. Ampliar auditoría con `actor_user_id`.
8. Adaptar frontend a login, sesión y “Mis estudios”.
9. Añadir tests de permisos antes de continuar con dashboard, sharing o borrado.

Permisos mínimos esperados:

- `admin`: puede ver todos los estudios, gestionar usuarios y acceder a vista administrativa.
- `researcher`: puede subir, listar, ver y descargar solo estudios propios.
- Usuario no autenticado: no puede acceder a endpoints sensibles.

Fuera de la primera implementación:

- Google/OIDC.
- ORCID.
- Rol `viewer` completo.
- Compartición mediante links.
- Email.
- Retención automática.
- Multiple upload.
- Cancelación de jobs en ejecución.
- 2FA.
- Cuotas.

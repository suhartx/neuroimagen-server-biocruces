# Seguridad

## Implementado En V0

- Validación de extensiones permitidas.
- Tamaño máximo configurable.
- Sanitización de nombres.
- Prevención básica de path traversal.
- `.env.example` sin secretos reales.
- `.env` ignorado por Git.
- Variables de entorno documentadas en `docs/configuration.md`.
- Logs técnicos separados de mensajes de usuario.
- Sin datos identificativos de pacientes en fixtures.
- Login local con JWT firmado y expiración configurable.
- Hash de contraseñas con PBKDF2-HMAC-SHA256 y salt aleatorio.
- Roles iniciales `admin` y `researcher`.
- Propietario por estudio mediante `owner_user_id`.
- Protección de endpoints de estudios y descargas.
- Auditoría de login, upload y download con usuario actor cuando aplica.
- Logs visibles en GUI con truncado.
- Cancelación de jobs en cola, retry de fallidos y borrado controlado con auditoría mínima.
- Dashboard admin protegido por rol.

Extensiones aceptadas por defecto: `.nii`, `.nii.gz`, `.dcm`, `.zip`, `.tar`, `.tar.gz`, `.gz`, `.json` y `.txt`.

La lista se configura mediante `ALLOWED_EXTENSIONS` y debe mantenerse alineada con `backend/app/core/config.py` y `docker-compose.yml`.

## Supuestos

- Uso inicial con datos anonimizados.
- Despliegue local o controlado para TFM, no expuesto como sistema hospitalario endurecido.

## Roadmap De Seguridad

La identidad local, permisos básicos, trazabilidad de jobs, dashboard admin y backup/restore local por CLI ya están implementados como base de TFM. Las siguientes mejoras de seguridad deben centrarse en exposición real y ciclo de vida de datos: retención, TLS, hardening de host/contenedores y una política de sesión más robusta si el sistema se comparte fuera de un entorno controlado.

### Autenticación Local Y Roles

Decisiones implementadas:

- Login local como primera opción.
- Usuarios creados por admin; sin registro público abierto.
- Roles iniciales `admin` y `researcher`.
- Asociación de cada estudio a un propietario mediante `owner_user_id`.
- Protección de endpoints de subida, listado, detalle, estado y descarga.
- Auditoría de login, upload y download.

Controles mínimos:

- No guardar passwords en texto plano.
- Usar hashing robusto.
- No devolver errores de login diferenciando si existe el email.
- Usar JWT con expiración.
- Cambiar `AUTH_SECRET_KEY` fuera de desarrollo.
- La API no arranca fuera de `development` si `AUTH_SECRET_KEY` conserva el valor por defecto o es demasiado corta.
- La GUI guarda el access token en `localStorage` para una implementación simple de TFM. Antes de exponer el sistema en un entorno compartido conviene evaluar cookie `HttpOnly/Secure/SameSite`, TTL menor y revocación de tokens.

Permisos esperados:

- `admin`: ve todos los estudios, gestiona usuarios, accede a dashboard y puede operar sobre jobs según política definida.
- `researcher`: ve y descarga solo estudios propios; puede cancelar o borrar los suyos si la política lo permite.

### Integraciones Futuras

- Google/OIDC queda como mejora futura para usuarios institucionales y debe poder convivir con login local.
- ORCID queda como mejora futura si el uso investigador gana peso.
- La restricción por dominio institucional debe configurarse por entorno, no hardcodearse.
- El rol `viewer` completo queda fuera de la implementación actual; para compartir informes se recomiendan enlaces firmados temporales con revocación y auditoría.
- 2FA queda fuera por ahora.

### Datos Y Descargas

- Los links compartidos futuros deben usar tokens firmados, caducidad configurable y revocación.
- Las descargas mediante token deben registrar auditoría.
- Los emails futuros deben enviar enlaces, no adjuntos pesados.
- Los logs visibles en GUI deben truncarse y evitar rutas internas sensibles.
- El borrado de estudios aplica soft delete y borrado físico, conservando auditoría mínima.

## Pendiente Antes De Entorno Hospitalario

- TLS real.
- Auditoría reforzada.
- Política de retención.
- Anonimización DICOM validada.
- Hardening del host y contenedores.
- Evaluación normativa y clínica.

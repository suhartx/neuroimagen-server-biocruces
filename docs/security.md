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

Extensiones aceptadas por defecto: `.nii`, `.nii.gz`, `.dcm`, `.zip`, `.tar`, `.tar.gz`, `.gz`, `.json` y `.txt`.

La lista se configura mediante `ALLOWED_EXTENSIONS` y debe mantenerse alineada con `backend/app/core/config.py` y `docker-compose.yml`.

## Supuestos

- Uso inicial con datos anonimizados.
- Sin autenticación en la primera versión.
- Despliegue local o controlado para TFM, no expuesto como sistema hospitalario endurecido.

## Roadmap De Seguridad

La siguiente mejora de seguridad debe ser **Fase 1 — Multiusuario básico**. La prioridad es resolver identidad, permisos y propietario por estudio antes de implementar compartición, notificaciones, cuotas o integración institucional.

### Fase 1: Login Local Y Roles

Decisiones recomendadas:

- Usar login local como primera opción.
- Crear usuarios desde admin; no habilitar registro público abierto.
- Implementar roles iniciales `admin` y `researcher`.
- Asociar cada estudio a un propietario mediante `owner_user_id`.
- Proteger endpoints de subida, listado, detalle, estado y descarga.
- Registrar auditoría de login, upload, download y delete.

Controles mínimos:

- No guardar passwords en texto plano.
- Usar hashing robusto.
- No devolver errores de login diferenciando si existe el email.
- Usar sesión o JWT con expiración.
- Documentar explícitamente la elección cookie/JWT antes de implementarla.

Permisos esperados:

- `admin`: ve todos los estudios, gestiona usuarios, accede a dashboard y puede operar sobre jobs según política definida.
- `researcher`: ve y descarga solo estudios propios; puede cancelar o borrar los suyos si la política lo permite.

### Integraciones Futuras

- Google/OIDC queda como mejora futura para usuarios institucionales y debe poder convivir con login local.
- ORCID queda como mejora futura si el uso investigador gana peso.
- La restricción por dominio institucional debe configurarse por entorno, no hardcodearse.
- El rol `viewer` completo queda fuera de la primera fase; para compartir informes se recomiendan enlaces firmados temporales con revocación y auditoría.
- 2FA queda fuera por ahora.

### Datos Y Descargas

- Los links compartidos futuros deben usar tokens firmados, caducidad configurable y revocación.
- Las descargas mediante token deben registrar auditoría.
- Los emails futuros deben enviar enlaces, no adjuntos pesados.
- Los logs visibles en GUI deben truncarse y evitar rutas internas sensibles.

## Pendiente Antes De Entorno Hospitalario

- TLS real.
- Autenticación y roles.
- Auditoría reforzada.
- Política de retención.
- Anonimización DICOM validada.
- Hardening del host y contenedores.
- Evaluación normativa y clínica.

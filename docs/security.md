# Seguridad

## Implementado En V0

- Validación de extensiones permitidas.
- Tamaño máximo configurable.
- Sanitización de nombres.
- Prevención básica de path traversal.
- `.env.example` sin secretos reales.
- `.env` ignorado por Git.
- Logs técnicos separados de mensajes de usuario.
- Sin datos identificativos de pacientes en fixtures.

## Supuestos

- Uso inicial con datos anonimizados.
- Sin autenticación en la primera versión.

## Pendiente Antes De Entorno Hospitalario

- TLS real.
- Autenticación y roles.
- Auditoría reforzada.
- Política de retención.
- Anonimización DICOM validada.
- Hardening del host y contenedores.
- Evaluación normativa y clínica.

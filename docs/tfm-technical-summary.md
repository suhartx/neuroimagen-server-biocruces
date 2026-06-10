# Resumen Técnico Para TFM

Este proyecto implementa una plataforma web containerizada para integrar procesamiento de neuroimagen por lotes con generación automática de resúmenes técnicos PDF y descarga de resultados.

La contribución principal no es el algoritmo de procesamiento, sino la capa software que permite operarlo de forma controlada, trazable y desacoplada. La arquitectura separa interfaz, API, persistencia, cola, worker y adaptador CLI, reduciendo acoplamiento y facilitando sustitución futura del procesador.

La integración con `compneuro-anatproc` prepara automáticamente BIDS para un T1w `.nii.gz`, ejecuta el flujo anatómico desde un worker basado en su imagen Docker, valida resultados `Preproc/BET` y `Preproc/ProbTissue`, renderiza NIfTI a PNG con FSL `slicer` y genera artefactos técnicos propios de la plataforma. El PDF resultante resume los resultados generados y no realiza interpretación clínica. El sistema no es todavía un producto sanitario completo y requiere validación clínica, autenticación institucional o política de sesión reforzada, hardening y políticas de datos antes de uso hospitalario real.

La decisión clave es mantener una API ligera y un worker especializado: FastAPI no procesa neuroimagen, Celery ejecuta tareas largas y `processor_adapter` encapsula el flujo externo.

## Evolución Planificada

El roadmap plantea una evolución incremental: primero identidad y permisos, después trazabilidad operativa, dashboard admin, backups/restore local, compartición segura, notificaciones, lotes, retención, flujos configurables, integración institucional y revisión clínica.

La plataforma incorpora una primera capa multiusuario con login local, roles `admin`/`researcher`, propietario por estudio, protección de endpoints y compartición temporal de PDFs técnicos. Esto desbloquea historial por usuario, control de acceso, auditoría real, administración y entrega controlada de informes sin modificar la frontera con el procesador externo. Integraciones como Google/OIDC, ORCID, email, cuotas o revisión clínica quedan justificadas como fases posteriores porque dependen de identidad, permisos y trazabilidad previas.

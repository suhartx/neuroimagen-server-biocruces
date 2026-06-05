# Resumen Técnico Para TFM

Este proyecto implementa una plataforma web containerizada para integrar procesamiento de neuroimagen por lotes con generación automática de resúmenes técnicos PDF y descarga de outputs.

La contribución principal no es el algoritmo clínico, sino la capa software que permite operarlo de forma controlada, trazable y desacoplada. La arquitectura separa interfaz, API, persistencia, cola, worker y adaptador CLI, reduciendo acoplamiento y facilitando sustitución futura del procesador.

La integración con `compneuro-anatproc` prepara automáticamente BIDS para un T1w `.nii.gz`, ejecuta el pipeline anatómico desde un worker basado en su imagen Docker, valida outputs `Preproc/BET` y `Preproc/ProbTissue`, renderiza NIfTI a PNG con FSL `slicer` y genera artefactos técnicos propios de la plataforma. El PDF resultante resume outputs generados y no realiza interpretación clínica. El sistema no es todavía un producto sanitario completo y requiere validación clínica, autenticación, hardening y políticas de datos antes de uso hospitalario real.

La decisión clave es mantener una API ligera y un worker especializado: FastAPI no procesa neuroimagen, Celery ejecuta tareas largas y `processor_adapter` encapsula el pipeline externo.

## Evolución Planificada

El roadmap plantea una evolución incremental: primero identidad y permisos, después trazabilidad operativa, dashboard admin, backups/restore, compartición segura, notificaciones, batches, retención, pipelines configurables, integración institucional y revisión clínica.

La siguiente fase lógica es multiusuario básico. Esta fase desbloquea historial por usuario, control de acceso, auditoría real y administración sin modificar la frontera con el procesador externo. Integraciones como Google/OIDC, ORCID, enlaces compartidos, email, cuotas o revisión clínica quedan justificadas como fases posteriores porque dependen de identidad, permisos y trazabilidad previas.

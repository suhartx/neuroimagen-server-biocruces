# Resumen Técnico Para TFM

Este proyecto implementa una plataforma web containerizada para integrar procesamiento de neuroimagen por lotes con generación automática de informes PDF.

La contribución principal no es el algoritmo clínico, sino la capa software que permite operarlo de forma controlada, trazable y desacoplada. La arquitectura separa interfaz, API, persistencia, cola, worker y adaptador CLI, reduciendo acoplamiento y facilitando sustitución futura del procesador.

La primera versión prioriza mantenibilidad, documentación, seguridad básica, trazabilidad y despliegue reproducible con Docker Compose. El sistema no es todavía un producto sanitario completo y requiere validación clínica, autenticación, hardening y políticas de datos antes de uso hospitalario real.

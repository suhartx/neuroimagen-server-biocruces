# Manual De Usuario

1. Entrá en la GUI.
2. Confirmá que la imagen está anonimizada.
3. Seleccioná una imagen anatómica T1w en formato `.nii.gz`.
4. Introducí un identificador BIDS de sujeto, por ejemplo `sub-O01`. Si lo dejás vacío, el sistema genera uno seguro.
5. Pulsá `Enviar a procesamiento`.
6. Esperá a que el estado pase de `En cola` a `Procesando` y luego a `Completado`. Puede tardar entre 10 minutos y 1 hora.
7. Descargá el PDF técnico y, si aparece, el ZIP de outputs.

Si el estado es `Fallido`, avisá al administrador y no uses ese resultado.

El PDF técnico lista metadatos, ficheros generados y PNG renderizados automáticamente desde outputs NIfTI mediante FSL `slicer`. No es un informe clínico validado y no debe usarse para tomar decisiones médicas sin revisión profesional.

Si el estado aparece como completado con avisos, el procesamiento principal terminó pero algún NIfTI pudo no renderizarse a PNG. En ese caso revisá el PDF y avisá al administrador si faltan imágenes esperadas.

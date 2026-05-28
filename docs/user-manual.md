# Manual De Usuario

1. Entra en la GUI.
2. Confirma que la imagen está anonimizada.
3. Selecciona una imagen anatómica T1w en formato `.nii.gz`.
4. Introduce un identificador BIDS de sujeto, por ejemplo `sub-O01`. Si lo dejas vacío, el sistema genera uno seguro.
5. Pulsa `Enviar a procesamiento`.
6. Espera a que el estado pase de `En cola` a `Procesando` y luego a `Completado`. Puede tardar entre 10 minutos y 1 hora.
7. Descarga el PDF técnico y, si aparece, el ZIP de outputs.

Si el estado es `Fallido`, avisa al administrador y no uses ese resultado.

El PDF técnico lista metadatos, ficheros generados y PNG renderizados automáticamente desde outputs NIfTI mediante FSL `slicer`. No es un informe clínico validado y no debe usarse para tomar decisiones médicas sin revisión profesional.

Si el estado aparece como completado con avisos, el procesamiento principal terminó pero algún NIfTI pudo no renderizarse a PNG. En ese caso revisa el PDF y avisa al administrador si faltan imágenes esperadas.

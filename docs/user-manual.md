# Manual De Usuario

1. Entra en la GUI.
2. Inicia sesión con tu email y contraseña.
3. Confirma que la imagen está anonimizada.
4. Selecciona una imagen anatómica T1w en formato `.nii.gz`.
5. Introduce un identificador BIDS de sujeto, por ejemplo `sub-O01`. Si lo dejas vacío, el sistema genera uno seguro.
6. Pulsa `Enviar a procesamiento`.
7. Espera a que el estado pase de `En cola` a `Procesando` y luego a `Completado`. Puede tardar entre 10 minutos y 1 hora.
8. Descarga el PDF técnico y, si aparece, el ZIP de outputs.

Si el estado es `Fallido`, avisa al administrador y no uses ese resultado.

El PDF técnico lista metadatos, ficheros generados y PNG renderizados automáticamente desde outputs NIfTI mediante FSL `slicer`. No es un informe clínico validado y no debe usarse para tomar decisiones médicas sin revisión profesional.

Si el estado aparece como completado con avisos, el procesamiento principal terminó pero algún NIfTI pudo no renderizarse a PNG. En ese caso revisa el PDF y avisa al administrador si faltan imágenes esperadas.

## Usuarios Y Roles

- `researcher`: puede subir estudios, ver su historial propio y descargar resultados propios.
- `admin`: puede ver todos los estudios y crear usuarios desde la GUI.

No hay registro público abierto. Los usuarios se crean desde una cuenta admin.

## Administración Básica

Para crear el primer admin, usar:

```bash
make create-admin EMAIL=admin@example.org
```

Después, el admin puede crear usuarios `researcher` o `admin` desde la GUI.

Quedan para fases posteriores la compartición mediante enlaces, notificaciones por email, subida múltiple, retención automática y revisión clínica formal.

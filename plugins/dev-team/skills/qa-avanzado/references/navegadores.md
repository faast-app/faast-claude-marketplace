# Otros navegadores y dispositivos

La suite corre en Chromium y en un perfil movil. Eso cubre la mayoria. **WebKit (Safari y todo
navegador en iPhone) y Firefox se agregan solo para los flujos criticos**, porque triplicar la
suite entera triplica el tiempo y los falsos rojos.

## Cuando aplica

- El flujo lo usa un **cliente externo** (portal de pagadores o proveedores): no eliges su navegador.
- El criterio nombra Safari, iPhone o iPad.
- La pantalla usa algo sensible al navegador: fechas nativas, descarga o subida de archivos,
  portapapeles, impresion/PDF, autocompletado, `dialog`, teclado numerico movil.

## Como

1. El flujo critico vive en un archivo `*.cross.spec.ts` (plantilla `tests/cross`).
2. `npm run test:cross` lo corre en chromium, webkit y firefox.
3. Lo que cambia entre navegadores se **reporta por navegador**: "en Safari el selector de
   fecha muestra mm/dd/aaaa" es un bug, con captura del navegador donde falla.

## Que mirar que solo aparece ahi

Fechas y numeros (formato del sistema, no del pais) · teclado en inputs numericos del
telefono · zoom al enfocar un campo de menos de 16 px en iPhone · barras del navegador movil
tapando el boton fijo de abajo · descarga de archivos en iPhone · foco visible y orden de
tabulacion en Safari · fuentes que no cargan y cambian el alto de las filas.

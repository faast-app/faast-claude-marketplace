# Texto de interfaz y de propuesta (taste-faast)

Di que es y que hace, con palabras que un desconocido entiende en cinco segundos. Cada frase
es una que le dirias en voz alta a un cliente.

## Cinco reglas

1. **El titulo nombra la cosa.** Pantalla: el objeto ("Operaciones", "Proveedores",
   "Liquidacion"). Landing o portada de deck: la categoria y para quien, en 2 a 8 palabras
   ("Confirming para pagadores en Peru"). Nunca un acertijo, una orden ni un estado de animo.
2. **Un dato duro en la primera pantalla:** una cifra, una fecha, un plazo, un estado.
3. **Todo titulo lleva un sustantivo que nombra algo:** el producto, una parte, una seccion
   ("Tasas y comisiones", "Seguimiento de la operacion") o un numero.
4. **Botones = verbo + lo que se obtiene,** 1 a 4 palabras, Title Case: Enviar Solicitud,
   Descargar Comprobante, Subir Facturas, Ver Liquidacion, Anular Operacion. Nunca "Aceptar",
   "OK", "Ver mas", "Saber mas", "Descubrir", "Explorar", "Click aqui".
5. **Pocas acciones, cada una con un solo nombre.** Una principal por vista; la misma
   palabra en encabezado, estado vacio y confirmacion.

## Version llana

| Vago | Llano |
| --- | --- |
| "Tu liquidez, potenciada" | Adelanto de facturas para proveedores |
| "Todo bajo control" | 12 operaciones en evaluacion, 3 observadas |
| "Algo salio mal" | No pudimos enviar la solicitud. Revisa tu conexion y vuelve a intentar. |
| "No hay datos" | Aun no hay operaciones. Crea la primera seleccionando tus facturas. |
| "¡Listo!" | Solicitud enviada: 3 facturas por S/ 10,000.00 |

## Microtexto de producto

- **Etiquetas** siempre visibles sobre el control; el placeholder es un ejemplo, no la etiqueta.
- **Ayuda** dice que acepta el campo ("11 digitos, sin guiones").
- **Error** bajo su campo: que esta mal y como corregirlo, con el ejemplo.
- **Vacio:** que esta vacio + el siguiente paso + la accion.
- **Confirmacion de accion sensible:** resumen (que, cuanto, a quien), verbo explicito en el
  boton ("Aprobar Desembolso"), y despues un comprobante.
- **Estados de negocio:** el mismo nombre en todas partes (no "Observada" en la tabla y "Con
  observaciones" en el detalle).
- **Numeros y fechas:** formato del pais del ambiente (S/ 10,000.00 · $ 10.000 · COP;
  dd/mm/aaaa); nunca un monto sin moneda.

## Lo que delata un texto escrito por un modelo (y su arreglo)

- **Palabras que reemplazan un dato** (vetadas): potente, robusto, intuitivo, sin fricciones,
  fluido, de vanguardia, de ultima generacion, revolucionario, transformador, integral,
  holistico, de clase mundial, potenciar, impulsar, desbloquear, elevar, reimaginar,
  ecosistema, sinergia, solucion (a secas), experiencia (a secas). Arreglo: pon el dato
  ("robusto" → "reintenta 3 veces y avisa"; "rapido" → "en 24 horas").
- **Frases de plantilla:** "En el mundo actual…", "Descubre el poder de…", "El futuro de X ya
  esta aqui", "Dile adios a…", "Ya seas A o B…", "Unete a miles de…", "No es solo un X, es un
  Y", "En pocos clics". Arreglo: borra la frase; lo que sigue suele ser el contenido.
- **Residuo:** lorem ipsum, `{{variable}}`, `[Nombre de la empresa]`, asteriscos o `##` en la
  pagina, "¡Claro!", "Espero que esto ayude". Cero tolerancia.
- **Formas repetidas:** la pregunta respondida al instante ("¿El resultado? Tres horas
  menos."), los dos puntos de revelacion, el gerundio colgado (", garantizando…"), tres
  adjetivos en fila, raya larga en cada oracion. Una vez puede pasar; repetido delata.
- **Sobrecorreccion:** frases de tres palabras en cada titulo, tono seco hasta sonar a
  telegrama. Llano no es cortante.

Revision final: lee el texto en voz alta. Lo que no dirias a un cliente frente a ti, se cambia.

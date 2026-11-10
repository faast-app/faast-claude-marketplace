# Revision de testabilidad (antes de que alguien programe)

El bug mas barato es el que se corrige en el criterio de aceptacion. El QA Lead revisa la HU
**cuando se refina o se planifica**, no cuando llega "lista para QA".

## Que revisa (10 minutos por HU)

| Pregunta | Mal | Bien |
|---|---|---|
| ¿El criterio tiene un resultado observable y exacto? | "El sistema valida el monto" | "Con monto 0 muestra «El monto debe ser mayor que 0» bajo el campo y no habilita Continuar" |
| ¿Estan los limites? | "Monto hasta el maximo" | "Maximo S/ 250,000.00 inclusive; 250,000.01 se rechaza" |
| ¿Dice que pasa cuando falla? | Solo el camino feliz | Un criterio por error de negocio relevante |
| ¿Hay reglas por pais, moneda o producto? | Implicito | Tabla: CL / PE / CO, con el valor de cada uno |
| ¿De que fecha depende? | "Al vencer" | "A las 00:00 del dia siguiente al vencimiento, hora del pais de la operacion" |
| ¿Quien puede y quien no? | "El usuario" | Rol que puede, rol que no, y que ve el que no |
| ¿Se puede preparar el dato? | Depende de datos "que deberian estar" | Dato semilla nombrado, o endpoint/fixture para crearlo |
| ¿Como se observa el resultado? | Solo en la base de datos | Pantalla, respuesta de API o evento verificable |

## Salida

Un bloque en el plan de pruebas (o comentario en el item, **en lenguaje de negocio**, por el PO):

```markdown
## Revision de testabilidad — HU-042
- Listo para probar: CA-1, CA-3
- Falta definir (bloquea el desarrollo): CA-2 — no dice que pasa con monto igual al maximo
- Dato de prueba a preparar (DBA): operacion aprobada con 2 facturas, pais PE
- Riesgo: R1 (calculo de intereses) → aplican puertas 8 (tiempo) y 11 (calidad de tests)
```

Lo que "falta definir" vuelve al PO como pregunta de negocio. QA no reescribe la HU: señala
el hueco. Una HU R1 con huecos no deberia entrar a desarrollo; se lo dices al Lead.

## Mapa de ejemplos (cuando la regla es enredada)

Para una regla con muchas combinaciones, propones al PO una tabla de **ejemplos concretos**
(regla → ejemplo → resultado) antes del desarrollo. Los ejemplos acordados son, tal cual, los
casos de prueba y los datos del test automatizado: negocio, desarrollo y QA prueban lo mismo.

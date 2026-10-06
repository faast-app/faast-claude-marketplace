# [Qué falla y dónde, en una frase] — Reporte de bug

**Correlativo:** `BUG-AAAA-NNN` · **Alcance:** Cliente [código] | Transversal · **Producto:** [factoring · confirming · …]
**Prioridad:** Crítica | Alta | Media | Baja — [criterio: qué proceso frena, cuántos usuarios]
**Estado:** Reportado | En validación QA | Confirmado | No reproducible — requiere información
**Reportado por:** [nombre, área, fecha] · **Ticket de origen:** [N° MDS]

> Un bug no se refina como requerimiento: se documenta con este formato y sigue el flujo de bugs
> (quien reporta prioriza, QA valida, desarrollo corrige). Sin los campos obligatorios, el bug se
> devuelve a quien lo reportó. Nada se inventa: lo que no está en el ticket ni confirma el usuario
> queda como "por completar".

## Datos del bug (obligatorios)

| | |
|---|---|
| **Qué ve mal el usuario** | [en una frase, como lo vive el negocio] |
| **Impacto** | Bloquea completamente · Se puede usar con errores · Solo visual · Solo a cierto perfil o cantidad — [a quién afecta y qué proceso frena] |
| **Ambiente** | [producción · pruebas · URL exacta] |
| **Usuario o rol afectado** | [perfil; sin datos personales] |
| **Módulo y pantalla** | [Menú › pantalla › sección] |
| **Desde cuándo** | [fecha aproximada; ¿antes funcionaba?; ¿cambió algo: versión, proceso, dato?] |
| **Frecuencia** | Siempre · A veces · Solo con ciertos datos — [cuáles] |
| **Solución temporal** | [workaround si existe; "No aplica" si no hay] |

## Evidencia (mínimo 2)

- [ ] Captura del error
- [ ] Captura del inspector (Console o Network) o enlace a Sentry / logs copiados
- [ ] Video corto, si el error es de secuencia
- [ ] Ejemplo concreto: ID de una operación o registro real donde ocurre

(Si falta evidencia, pedirla en una sola lista; no suponer.)

## Pasos para reproducir (como usuario)

1. Ambiente / URL: …
2. Usuario o rol: …
3. Navegación: Menú › opción › …
4. Acción: …
5. **Resultado (error):** …
6. **Esperado:** … — `[A §x]` / `[C especificación §x]` / release [n] que dice cómo debería funcionar

## Si es backend (completar si se sabe; si no, lo completa desarrollo)

Microservicio · endpoint · código HTTP · Request ID / Trace ID · payload · enlace a Sentry

## Información adicional

Navegador y versión · sistema operativo · consistente o intermitente · fecha y hora · observaciones

## Etiquetas para GitHub

`tipo:bug` · `cliente:{código}` o `alcance:transversal` · `producto:{…}` · `prioridad:{…}` ·
`origen:{correo|reunion|ticket}` · `mesa:BUG-AAAA-NNN` · (QA completa: área, navegador)

## Criterios de resolución

(Los completa QA al validar la corrección: mismos pasos, resultado esperado observado, evidencia nueva.)

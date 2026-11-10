---
name: qa-avanzado
description: Practicas avanzadas y actuales de QA para el equipo QA de dev-team, que se suman a sus 7 puertas - revision de testabilidad antes de desarrollar (shift-left), tiempo controlado para vencimientos, mora y fin de mes, rendimiento percibido contra presupuesto (Core Web Vitals) y humo de carga de API, otros navegadores para flujos criticos, calidad de los tests del desarrollador (mutacion y cobertura del cambio), estructura accesible como foto, y el indice de confianza del veredicto. Cargala al planificar pruebas de una HU de riesgo alto o medio, al revisar criterios antes del desarrollo, cuando la HU depende de fechas, de rendimiento o de varios navegadores, y al consolidar el informe de QA.
---

# QA avanzado (dev-team)

Las **7 puertas** del QA Lead siguen siendo la base y no cambian. Esta skill agrega lo que un
equipo de QA actual hace ademas, **cuando el riesgo lo justifica**: nada de aqui es ceremonia
para toda HU. Cada practica dice cuando aplica; lo que no aplica se anota `N/A` con su motivo.

| Practica | Cuando aplica | Quien | Referencia |
|---|---|---|---|
| **Revision de testabilidad** (antes de desarrollar) | Toda HU R1/R2, al refinar o planificar | qa (Lead) | `references/shift-left.md` |
| **Tiempo controlado** | La HU depende de la fecha u hora: vencimientos, mora, dias habiles, fin de mes, expiracion de sesion | qa-frontend, qa-backend | `references/tiempo-y-fechas.md` |
| **Rendimiento percibido** | Pantalla nueva o tocada de uso diario, o el criterio lo pide | qa-frontend | `references/rendimiento.md` |
| **Humo de carga de API** | Endpoint R1 nuevo, o cambio de consulta/indice/paginacion | qa-backend | `references/rendimiento.md` |
| **Otros navegadores** | Flujos R1 que usa un cliente externo (portales), o el criterio nombra Safari/iPhone | qa-frontend | `references/navegadores.md` |
| **Calidad de los tests del dev** | HU R1 con logica de calculo (montos, tasas, intereses, fechas) | qa (Lead) lee el reporte | `references/calidad-de-tests.md` |
| **Estructura accesible como foto** | Pantalla con formulario o tabla que ya paso axe | qa-frontend | plantilla `tests/a11y` |
| **Indice de confianza** | Siempre, en el informe consolidado | qa (Lead) | `references/confianza.md` |

## Como se integra con las puertas

- Son **puertas condicionales** (8 a 11): se evaluan solo si la practica aplica a la HU. Una
  que aplica y falla es **RECHAZADA**, igual que las 7. Una que no aplica va `N/A — motivo`.
  - **8. Tiempo:** los casos dependientes de fecha pasan con reloj controlado, incluidos los
    limites (dia anterior, dia exacto, dia siguiente; fin de mes; cambio de año).
  - **9. Rendimiento:** la pantalla cumple su presupuesto (LCP, CLS, peso) y, si hay endpoint
    R1, el humo de carga cumple su p95.
  - **10. Otros navegadores:** el flujo critico pasa en WebKit y Firefox.
  - **11. Calidad de tests del dev:** el reporte de mutacion/cobertura del cambio cumple el
    umbral, o queda registrada la deuda con responsable.
- La suite de plantilla (`templates/e2e-faast`) ya trae lo necesario: `tests/tiempo`,
  `tests/perf`, `tests/cross`, la foto de accesibilidad en `tests/a11y`, `api/contract.mjs`
  (sin bash) y un workflow que reparte la suite en 3 maquinas y une el reporte.
- QA **sigue sin depurar y sin tocar codigo de producto**: mide, compara con el umbral y
  reporta. El desarrollador corrige.

## Reglas

- **El riesgo decide la profundidad.** R3 no paga rendimiento ni otros navegadores salvo que
  el criterio lo pida. Lo que se omite se escribe en "Fuera de alcance — motivo".
- **Umbrales del proyecto, no inventados:** `config.json` → `qa.umbrales`
  (`{"lcpMs": 2500, "cls": 0.1, "pesoKb": 1500, "apiP95Ms": 800, "mutacion": 60}`); si no
  existen, se usan esos valores por defecto y se dice en el informe.
- **Medir en el mismo ambiente y dos veces:** un numero de rendimiento es valido si dos
  corridas seguidas quedan dentro del presupuesto. Una sola medicion es una anecdota.
- **Cada medicion es evidencia:** el JSON de la medicion va a `evidence/{HU}/` y se cita en
  el bloque del criterio.

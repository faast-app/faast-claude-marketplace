---
name: vercel-react-patterns
description: Guias de ingenieria React de Vercel para el frontend de dev-team - React Best Practices (70 reglas de rendimiento por impacto - cascadas async, tamaño de bundle, servidor, fetching en cliente, re-renders, render, JS) y Composition Patterns (evitar props booleanas, compound components, estado en providers, variantes explicitas, APIs de React 19), con las copias fijadas y como se aplican sobre la libreria @faast-app/ui. Cargala al implementar o revisar pantallas React/Next.js, al revisar un PR de frontend y al proponer un componente nuevo para la libreria.
---

# Vercel React patterns (dev-team)

Dos guias de Vercel Engineering, copiadas **sin modificar** (MIT, `vercel-labs/agent-skills`,
commit `1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62`, revisado 2026-11-10):

| Referencia | Contenido | Cuando leerla |
| --- | --- | --- |
| `references/react-best-practices.upstream.md` | 70 reglas en 8 categorias, con ejemplo incorrecto/correcto | Implementar o revisar pantallas, data fetching, rendimiento |
| `references/composition-patterns.upstream.md` | Arquitectura de componentes, estado, patrones, React 19 | Diseñar la API de un componente, refactorizar props booleanas |

Son largas: **no las leas enteras**. Busca por prefijo de regla (`grep -n "async-" …`) y lee
la seccion que toca tu cambio.

## Prioridad (por impacto)

1. **Cascadas async** (`async-*`, CRITICO): `Promise.all` para lo independiente, `await` en
   la rama que lo usa, limites de `Suspense`.
2. **Tamaño de bundle** (`bundle-*`, CRITICO): imports directos (sin barrels), `import()`
   dinamico para lo pesado, terceros diferidos.
3. **Servidor** (`server-*`, ALTO; solo Next.js/RSC): autenticar server actions como rutas
   API, `React.cache()`, serializar lo minimo al cliente.
4. **Fetching en cliente** (`client-*`): deduplicar peticiones, listeners pasivos.
5. **Re-renders** (`rerender-*`): estado derivado en render y no en efectos, `setState`
   funcional, sin componentes definidos dentro de componentes, logica de interaccion en el
   handler y no en `useEffect`.
6. **Render** (`rendering-*`), **JS** (`js-*`), **avanzado** (`advanced-*`): al final y con
   medicion.

Composicion: nada de props booleanas que cambian el comportamiento (`isCompact`, `withIcon`)
→ variantes explicitas o composicion · componentes compuestos con contexto compartido · el
provider es el unico que sabe como se guarda el estado · `children` antes que `renderX`.

## Como aplica en FaaST

- **La UI sale de `@faast-app/ui`** (skill `dev-team:libreria-faast`). Estas guias gobiernan
  el codigo de la aplicacion alrededor de los componentes, no reemplazan componentes.
- Importa del punto de entrada de la libreria (`import { Button } from '@faast-app/ui'`): es
  ESM con `sideEffects` declarado y hace tree-shaking; la regla anti-barrel aplica a los
  barrels **de la aplicacion**.
- Iconos solo con `<Icon name>`; la aplicacion no importa `lucide-react`.
- La mayoria de los frontends FaaST son SPA con Vite: las reglas `server-*` y de hidratacion
  aplican solo si el proyecto usa Next.js/SSR (lo dice `architecture.md`).
- React 18.2 y 19 estan soportados por la libreria: las reglas `react19-*` solo si el
  proyecto esta en 19.
- **Un componente nuevo para la libreria** se diseña con Composition Patterns desde el
  inicio (variantes explicitas, partes componibles como `Card` + `CardHeader`), con la
  ficha de `dev-team:libreria-faast` seccion 5.
- Dinero, fechas, idempotencia y auditoria: manda `dev-team:ingenieria-faast`.

## En una revision de PR de frontend

Reporta por regla: `archivo:linea — regla-id — que pasa — arreglo`. Solo lo que tiene
impacto en este cambio; no pidas `useMemo` por reflejo (`rerender-simple-expression-in-memo`).
Lo CRITICO bloquea; lo MEDIO se sugiere; lo BAJO solo con evidencia de medicion.

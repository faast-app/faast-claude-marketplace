# Frontend — detalle

Para pantallas nuevas, el diseño aprobado (`.coordination/design/{DSN}/`) es la fuente de
verdad visual. Las skills `a11y-checklist` y `design-tokens-dtcg` del plugin profundizan
accesibilidad y tokens.

## 1. Estados de cada pantalla y de cada dato remoto

Toda vista que depende de datos remotos implementa los cuatro estados: **loading**
(skeleton con las dimensiones finales, sin saltos de layout), **empty** (mensaje y accion
siguiente, no una tabla vacia), **error** (mensaje humano + reintentar + `traceId` copiable
para soporte; nunca el JSON crudo) y **success**. Las mutaciones tienen ademas
**pending** (boton deshabilitado + indicador; evita doble envio de un giro) y confirmacion de
resultado (toast o estado en pantalla).

- **Error boundaries** por ruta/zona (React `ErrorBoundary`, Angular `ErrorHandler`, Vue
  `onErrorCaptured`): un widget roto no tumba la pantalla. En microfrontends, un remote que no
  carga muestra un fallback, el shell sigue vivo.
- Mapear Problem Details (`type`/`code`, `errors` de validacion) a mensajes por campo y
  mensajes globales; `401` → flujo de sesion; `403` → pantalla de sin permiso; `409/412` →
  "otro usuario modifico este registro, recarga"; `429` → espera; `5xx` → error generico.

## 2. Datos remotos

- Servidor como fuente de verdad con **TanStack Query** (o el equivalente del repo:
  RxJS/HttpClient + signals en Angular, Pinia + composables en Vue): cache por clave, `staleTime`
  explicito, invalidacion tras mutaciones, `retry` solo en lecturas.
- Cliente HTTP tipado por servicio, tipos derivados del OpenAPI (`openapi-typescript`/
  `orval`/generador del repo). Nunca `any` en respuestas.
- Cancelacion de requests al desmontar/cambiar filtros (`AbortController`); debounce en
  busquedas.
- Las mutaciones que mueven dinero envian `Idempotency-Key` (uuid generado al abrir el
  formulario, no por click) y nunca se reintentan automaticamente.

## 3. Formularios

- Validacion **esquematica** compartida entre tipo y regla: **zod** (+ React Hook Form con
  `zodResolver`, o TanStack Form), Reactive Forms con validadores tipados en Angular,
  VeeValidate + zod en Vue.
- La validacion del front es UX; **la del backend es la autoridad**: mostrar los `errors` del
  Problem Details en sus campos.
- Mensajes de error junto al campo, asociados (`aria-describedby`), en lenguaje del usuario,
  y un resumen al enviar con foco en el primer error.
- Campos de RUT/RUC/NIT: formateo mientras se escribe y validacion de DV como ayuda; se envia
  normalizado.
- Campos de monto: entrada como texto con mascara por locale; se envia como **string decimal**
  normalizado (`"1250000"`, `"1250.50"`); nunca se calcula plata con `number` en el front
  (los totales los devuelve el backend; si se muestran previsualizaciones, con libreria decimal
  y rotuladas como estimadas).
- Confirmacion explicita (resumen + confirmar) antes de acciones irreversibles en
  productivo (giro, pago, anulacion).

## 4. Formato por pais (locale)

```ts
const fmtMonto = (monto: string, moneda: 'CLP'|'PEN'|'COP'|'USD', locale: 'es-CL'|'es-PE'|'es-CO') =>
  new Intl.NumberFormat(locale, {
    style: 'currency', currency: moneda,
    minimumFractionDigits: moneda === 'CLP' ? 0 : 2,
    maximumFractionDigits: moneda === 'CLP' ? 0 : 2,
  }).format(Number(monto))   // solo para MOSTRAR; jamas para calcular
```
- `es-CL`: `$ 1.250.000` (punto de miles, sin decimales en CLP). `es-PE`: `S/ 1,250.50`.
  `es-CO`: `$ 1.250.000,50` (verifica la regla de decimales del producto). Prueba el formato
  con tests: los separadores difieren entre locales y versiones de ICU.
- Fechas: `Intl.DateTimeFormat(locale, { timeZone: 'America/Santiago' | 'America/Lima' |
  'America/Bogota' })`. **Fechas de negocio** (`"2026-03-31"`) no se parsean con
  `new Date("2026-03-31")` (lo toma como UTC y en America/* muestra el dia anterior): parsea
  como fecha local (`date-fns` `parseISO` + formato sin TZ, `Temporal.PlainDate` donde el
  navegador objetivo lo soporte, o split manual).
- Textos en español neutro o del pais segun producto; numeros y fechas nunca concatenados a mano.

## 5. Accesibilidad WCAG 2.2 AA (minimo, no opcional)

- Semantica primero: `button` para acciones, `a` para navegacion, encabezados en orden,
  landmarks (`header`, `nav`, `main`), tablas con `th`/`scope` y `caption`.
- Todo operable con teclado, foco **visible** y no tapado por headers fijos (2.4.11), orden de
  foco logico, sin trampas; modales con foco atrapado y retorno al cerrar.
- Labels reales en inputs (no solo placeholder), `aria-invalid` + `aria-describedby` en errores,
  cambios asincronos anunciados (`aria-live="polite"` para toasts/resultados).
- Contraste 4.5:1 texto (3:1 texto grande y componentes UI); no transmitir informacion solo con
  color (estados de operacion con texto/icono).
- Objetivos tactiles minimo 24×24 px (2.5.8); arrastrar siempre con alternativa (2.5.7);
  autenticacion sin pruebas cognitivas (3.3.8); no pedir dos veces lo ya ingresado (3.3.7).
- `prefers-reduced-motion` respetado; zoom 200% y reflow a 320px sin perder funcion.
- Verificacion: axe (en tests y en Playwright), navegacion solo con teclado, y lector de
  pantalla en los flujos criticos.

## 6. Seguridad en el navegador

- **XSS**: nunca `dangerouslySetInnerHTML`/`innerHTML`/`v-html`/`bypassSecurityTrust*` con
  datos del usuario o del backend; si es imprescindible, `DOMPurify`. URLs dinamicas
  validadas (nada de `javascript:`).
- **Tokens fuera de localStorage/sessionStorage**: cookie `HttpOnly; Secure; SameSite` o en
  memoria con refresh por cookie. Nada sensible en la URL (query strings quedan en logs).
- **CSP** compatible: sin scripts inline ni `eval`; la config de runtime (`env.js`) solo con
  valores publicos (URLs), jamas secretos — todo lo que llega al navegador es publico.
- CSRF si se usan cookies (token anti-CSRF o `SameSite=Strict/Lax` + verificacion de origen).
- Dependencias: `npm audit`/SCA en CI, versiones fijadas con lockfile, nada de paquetes sin
  mantenimiento para cosas triviales.
- Datos personales: no persistir en `localStorage`, no enviarlos a analitica, enmascarar en
  pantalla cuando no hacen falta completos.

## 7. Rendimiento (Core Web Vitals)

- Objetivos (p75): **LCP < 2.5 s**, **INP < 200 ms**, **CLS < 0.1**.
- Code splitting por ruta (`lazy`/`loadComponent`/rutas async) y por widgets pesados (graficos,
  editores, PDF); presupuesto de bundle en CI cuando el repo lo tenga.
- Imagenes con dimensiones, formatos modernos y `loading="lazy"` fuera del primer viewport;
  fuentes con `font-display: swap` y precarga de la principal.
- Tablas grandes paginadas en servidor o virtualizadas (TanStack Virtual); nada de renderizar
  miles de filas.
- Memoizacion solo donde se midio el problema (React Compiler en React 19 si el repo lo usa);
  evitar re-renders masivos por contextos globales.
- Medir con Lighthouse/Web Vitals en la build de produccion, no en dev.

## 8. Fidelidad al diseño

Implementas exactamente el prototipo aprobado: medidas, tokens, tipografia, estados y
movimiento. Todo valor visual sale de los tokens (CSS variables/Tailwind generados); un token
faltante se pide al design-engineer. Si no hay diseño aprobado para una pantalla nueva, no se
implementa "a ojo": `blocked` y pedido al Lead. QA compara contra el prototipo (regresion visual).

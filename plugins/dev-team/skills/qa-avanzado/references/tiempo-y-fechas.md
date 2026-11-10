# Tiempo controlado

En una fintech casi todo lo caro depende de la fecha: vencimientos, mora, intereses por dia,
dias habiles y feriados por pais, cierre de mes, expiracion de sesion. Esperar a que llegue el
dia no es probar, y un test que depende de "hoy" pasa un lunes y falla un domingo.

## Los limites que siempre se prueban

| Regla | Casos |
|---|---|
| Vencimiento | dia anterior · dia exacto (23:59) · dia siguiente (00:00) |
| Mes | dia 28/29/30/31 · febrero en año bisiesto y no bisiesto · paso de mes |
| Año | 31 de diciembre → 1 de enero (correlativos, periodos tributarios) |
| Dia habil | viernes → lunes · feriado del pais de la operacion (CL, PE y CO no comparten feriados) |
| Zona horaria | la misma operacion vista desde otro pais; nunca asumir la zona del servidor |
| Duracion | sesion a 1 minuto de expirar · token vencido a mitad de un formulario |

## En la interfaz: el reloj del navegador (Playwright)

```ts
await page.clock.install({ time: new Date('2026-06-30T23:59:00-04:00') });
await page.goto('/operaciones/OP-2026-0418');
await page.clock.fastForward('00:02:00');   // cruza la medianoche sin esperar
await page.reload();
```

`install` fija la fecha antes de cargar la pagina; `fastForward` adelanta; `setFixedTime` la
congela. Ejemplo completo en la plantilla: `tests/tiempo/vencimientos.clock.spec.ts`.

Esto controla **lo que calcula el navegador** (contadores, avisos, formato). Si la regla la
calcula el servidor, el reloj del navegador no la cambia.

## En el servidor: datos fechados

Para reglas que calcula el backend (mora, intereses) el tiempo se controla con **datos**:
operaciones semilla con vencimiento ayer, hoy y mañana **relativas a la fecha de la corrida**
(el DBA las siembra con scripts idempotentes; qa-backend las consulta en solo lectura). Si el
ambiente de pruebas permite fijar la fecha del sistema, se usa y se anota; nunca se toca la
fecha de un ambiente compartido sin el OK del usuario.

## Reporte

Cada caso de tiempo dice la fecha simulada, la zona y el resultado exacto:
`CA-1 › C05 · 2026-07-01 00:01 America/Lima → estado "En mora", interes dia 1 = S/ 3.42`.

# Calidad de los tests del desarrollador (mutacion y cobertura del cambio)

"Los tests pasan" no dice si los tests **detectarian un error**. En una HU R1 con calculo
(montos, tasas, intereses, comisiones, fechas) el QA Lead pide y lee dos señales. No las
produce ni toca el codigo: son evidencia que entrega el desarrollador con su handoff.

## 1. Cobertura del cambio (no del repo)

Que lineas **del diff** ejecutan los tests. El 80 % global de un repo no dice nada de las 40
lineas nuevas del calculo. Umbral por defecto: 90 % de las lineas cambiadas en logica de
negocio R1; lo no cubierto se justifica linea por linea.

## 2. Pruebas de mutacion (en los archivos del cambio)

La herramienta altera el codigo a proposito (`>` por `>=`, `+` por `-`, quita una condicion) y
corre los tests: si siguen pasando, ese error **no lo detecta nadie**. Se corre solo sobre los
archivos del cambio, no sobre el repo.

| Stack | Herramienta | Comando tipico (sobre el cambio) |
|---|---|---|
| TypeScript / JavaScript | StrykerJS | `npx stryker run --mutate "src/calculo/**/*.ts"` |
| .NET | Stryker.NET | `dotnet stryker --mutate "**/Calculo*.cs"` |
| Python | mutmut | `mutmut run --paths-to-mutate src/calculo` |
| Java | PIT | `mvn org.pitest:pitest-maven:mutationCoverage -DtargetClasses=...` |

- Umbral por defecto: **60 %** de mutantes eliminados en los archivos del cambio
  (`qa.umbrales.mutacion`). Los mutantes vivos en una regla de dinero se listan uno por uno:
  cada uno es un caso de prueba que falta.
- Si el repo no tiene la herramienta: **no se bloquea la HU por eso**. Se registra la deuda
  ("sin señal de mutacion en el modulo de calculo") con responsable, y la puerta 11 queda
  `N/A — herramienta no instalada`. Instalarla es una tarea del Lead, no de QA.

## Como lo usa QA

Cada mutante vivo relevante se traduce a un caso del plan: si cambiar `>` por `>=` en el tope
de monto no rompe ningun test, falta el caso del valor limite — y QA lo prueba a mano y lo
reporta. Asi la mutacion alimenta el diseño de casos, no es solo un numero.

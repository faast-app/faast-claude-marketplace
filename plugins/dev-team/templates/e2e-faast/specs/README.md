# specs/ — planes de prueba en Markdown (Playwright Test Agents)

Aqui deja el **planner** (`🎭 planner`, generado con `npm run agents:init`) el plan de
cada HU: `specs/hu-{nnn}.md`. El QA Lead lo revisa y lo referencia desde
`.coordination/test-plans/hu-{nnn}.md`. El **generator** convierte cada plan en
`tests/hu-{nnn}-{slug}.spec.ts` (1 test por criterio, convencion `CA-N:`).
El **healer** solo se usa en regresion y NUNCA cambia una asercion esperada.

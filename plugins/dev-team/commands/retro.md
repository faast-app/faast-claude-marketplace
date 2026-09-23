---
description: Retrospectiva del sprint - reune datos reales (velocidad, veredictos revertidos, bloqueos, latencia de handoffs, bugs), facilita que salio bien / que mejorar, y convierte los acuerdos en acciones concretas con responsable. El PO aplica las mejoras de backlog desde el proximo sprint. Uso - /dev-team:retro [sprint N]
argument-hint: '[actual | sprint N]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Retro: retrospectiva con datos y acciones

Sprint: $ARGUMENTS (por defecto el actual)

Cierra el ciclo Scrum: mira los datos del sprint, saca aprendizajes y los convierte en acciones
concretas — no en buenas intenciones. La facilita el Lead con apoyo del PO.

## Paso 1 — Datos del sprint (de las fuentes reales, no impresiones)
De `.coordination/metrics/activity.jsonl`, `sprint-actual.md`, `backlog.md`, handoffs y evidencia:
- **Compromiso vs. entregado**: HUs comprometidas, completadas, arrastradas (con story points).
- **Calidad**: tasa de veredictos revertidos de QA (`reopened` sobre HUs aprobadas; meta 0,1 %),
  bugs encontrados/escapados a produccion, revalidaciones que siguieron fallando.
- **Flujo**: bloqueos (`blocked`) y cuanto duraron, handoffs con mayor latencia (pedido → atendido),
  gates de merge que frenaron.
- **Costo**: consumo por agente/modelo (referencia a `/dev-team:team-metrics`), para proponer
  ajustes de modelo si algo esta sobredimensionado.

## Paso 2 — Facilitar (que salio bien / que mejorar)
Presentar los datos y guiar tres columnas, cortas y honestas:
- **Siguio bien** (mantener): lo que funciono y hay que conservar.
- **A mejorar** (duele): cuellos de botella, retrabajo, bloqueos recurrentes — con el dato que lo respalda.
- **Ideas** (probar): experimentos para el proximo sprint.
Sin buscar culpables: se mira el proceso, no a las personas.

## Paso 3 — Acciones concretas (lo que hace util una retro)
Cada mejora se convierte en una ACCION con responsable, no en un deseo:
```
| Accion | Responsable (rol) | Como se vera que funciono | Cuando |
|--------|-------------------|---------------------------|--------|
| Reproducir bugs siempre en qa, no en desa | qa | 0 veredictos invalidos por ambiente | prox sprint |
```
- Las que afectan como se escribe el backlog las aplica el **PO** desde el proximo sprint.
- Las de proceso tecnico (CI, gates, ramas) las toma el rol dueño via handoff.
- Guardar la retro en `.coordination/retros/retro-sprint-{n}.md` y registrar los acuerdos como
  handoffs a sus responsables. Opcional: el tech-writer la ingiere a la wiki (`decisiones/`).

## Salida al usuario
```
Retro Sprint {n}
Entregado: {x}/{y} HUs ({z} arrastradas) · Veredictos revertidos: {%} · Bloqueos: {n} ({horas})
Siguio bien: {1-3 puntos}
A mejorar: {1-3 puntos con su dato}
Acciones (con responsable): {tabla}
```

## Reglas
- La retro se apoya en DATOS reales, no en impresiones sueltas.
- Cada aprendizaje sale con una accion concreta y un responsable, o no cuenta.
- Se mira el proceso, no a las personas.
- Los acuerdos quedan trazables (archivo + handoffs); el PO aplica los de backlog desde el proximo sprint.

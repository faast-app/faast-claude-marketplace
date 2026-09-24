---
description: Auditoria de seguridad del repo/proyecto con el equipo de ciberseguridad (cybersec Lead + appsec + cloudsec). Revision estatica de codigo, dependencias, secretos e infra. Para pruebas ACTIVAS sobre la app desplegada (ethical hacking) usa /dev-team:pentest.
argument-hint: 'deps | secrets | auth | headers | injection | docker | inter-service | full  [repo/servicio]'
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecuta su
> procedimiento en la sesion actual (el contexto ya esta cacheado). NUNCA lo
> corras dentro de un subagente ni lo invoques via Agent/Task — eso recarga todo
> el contexto desde cero y quema tokens. Solo se delegan los AGENTES del equipo,
> y unicamente cuando este procedimiento lo indica.


# Auditoria de seguridad (revision estatica con el equipo)

Encargo: $ARGUMENTS

Este comando corre la auditoria ESTATICA (sin atacar la app viva): codigo, dependencias,
secretos e infraestructura. Es rapido y no necesita Rules of Engagement de red — solo
confirmar que el repo/servicio esta en el alcance. **Para pruebas ACTIVAS** (IDOR, bypass de
auth, inyeccion en runtime, SSRF sobre la app desplegada) usa `/dev-team:pentest`, que exige
autorizacion y alcance firmados.

## Que audita cada foco
1. **deps** — dependencias vulnerables (SCA): `dotnet list package --vulnerable` · `npm audit` · `pip-audit` · OWASP dependency-check (Java) → **appsec**
2. **secrets** — credenciales hardcodeadas (grep + historial git, avisar rotacion) → **appsec**
3. **auth** — revision del codigo de login/registro/permisos/JWT/cripto e IDOR en el origen → **appsec**
4. **headers** — headers HTTP de seguridad, TLS, CORS → **cloudsec**
5. **injection** — patrones de SQL injection, XSS, deserializacion, SSRF en el codigo → **appsec**
6. **docker** — Dockerfile/imagen (root, secretos en capas, healthcheck, base pinneada) → **cloudsec**
7. **inter-service** — comunicacion entre servicios (mTLS, API keys, validacion de token, red) → **cloudsec**
8. **full** — todo lo anterior; el **cybersec** (Lead) reparte a appsec + cloudsec en paralelo y consolida

## Flujo
1. El **cybersec** (Cybersec Lead) confirma el alcance (repo/servicio) y reparte por handoff:
   los focos de codigo a **appsec**, los de infra a **cloudsec**. Pueden correr EN PARALELO
   (los invoca el Lead / la sesion principal). Si el foco es unico, lo ejecuta el especialista directo.
2. Cada especialista aplica la skill `security-testing`, deja evidencia en
   `.coordination/evidence/PENTEST-{id}/{area}/` y su handoff de hallazgos al Cybersec Lead.
3. El Cybersec Lead consolida: verifica, puntua CVSS 3.1, prioriza y arma el reporte.

## Para cada hallazgo
- Severidad: Critico | Alto | Medio | Bajo (CVSS 3.1)
- Ubicacion exacta: archivo:linea (o componente/config)
- Impacto: que puede pasar si se explota (en terminos de negocio)
- Remediacion: ejemplo concreto del fix
- Si necesita confirmacion en runtime: se marca para `/dev-team:pentest`

## Salida
- Reporte consolidado en `.coordination/handoffs/cybersec-to-lead-{fecha}.md`
- Los hallazgos confirmados se registran como items (via PO) con evidencia embebida
- Para el informe formal en PDF: `/dev-team:security-report PENTEST-{id}`
- Los hallazgos Criticos/Altos se reportan al Lead de inmediato; el gate de merge no aprueba con ellos abiertos

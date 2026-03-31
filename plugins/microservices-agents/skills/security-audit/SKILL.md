---
description: Ejecuta auditoria de seguridad en el repo actual. Usa el agente cybersec.
---

Ejecuta auditoria de seguridad. Pregunta que auditar:

1. **deps** — Dependencias vulnerables (`dotnet list package --vulnerable` + `npm audit` + `pip-audit`)
2. **secrets** — Buscar credenciales hardcodeadas con grep
3. **auth** — Auditar flujo completo de login/registro/permisos
4. **headers** — Verificar headers HTTP de seguridad
5. **injection** — Buscar SQL injection y XSS patterns en codigo
6. **docker** — Auditar Dockerfile (root, secrets, healthcheck)
7. **inter-service** — Auditar comunicacion entre servicios (mTLS, API keys)
8. **full** — Todo lo anterior

Invoca al agente `cybersec` para ejecutar la auditoria.

Para cada hallazgo:
- Severidad: Critico | Alto | Medio | Bajo
- Ubicacion exacta: archivo y linea
- Impacto: que puede pasar si se explota
- Remediacion: codigo de ejemplo del fix

Genera reporte en `.coordination/handoffs/cybersec-to-lead-{fecha}.md`

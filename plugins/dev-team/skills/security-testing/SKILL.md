---
name: security-testing
description: Metodologia profesional de pruebas de seguridad ofensiva para el equipo de ciberseguridad de dev-team - Rules of Engagement y alcance, fases PTES, OWASP WSTG / Top 10 2021 / API Security Top 10 2023 / MASVS, checklist por clase de vulnerabilidad, prueba de concepto reproducible, puntuacion CVSS 3.1, cadena de custodia de la evidencia y estructura del informe. Cargala antes de planear o ejecutar cualquier pentest, auditoria de seguridad o informe de hallazgos.
---

# Pruebas de seguridad ofensiva — metodologia (dev-team)

Esta skill es el marco de trabajo del equipo de ciberseguridad. Sirve tanto para
la revision estatica (appsec) como para la prueba activa autorizada (pentester) y
la auditoria de infraestructura (cloudsec). El objetivo es entregar un producto
seguro con evidencia objetiva, no "sensacion de seguridad".

## 0. Regla cero — autorizacion y alcance (INNEGOCIABLE)

Ninguna prueba ACTIVA (enviar payloads, forzar auth, explotar, escanear) empieza sin:
1. **Autorizacion escrita y confirmada** por el dueño del proyecto/usuario, con fecha.
2. **Alcance explicito (Rules of Engagement)**: que activos ENTRAN y cuales quedan
   FUERA (dominios, IPs, repos, servicios), que tecnicas se permiten, ventana horaria,
   ambiente objetivo (preferente NO productivo), y contactos de escalamiento.
3. **Propiedad verificada**: solo se prueba lo que es de FAAST / del proyecto (de
   `config.json` o del alcance firmado). Jamas un tercero, un proveedor, un dominio
   ajeno, ni infraestructura que no sea del cliente aunque "parezca" del proyecto.

La revision ESTATICA (leer codigo, dependencias, IaC, configs de un repo del proyecto)
no necesita RoE de red, pero SI la confirmacion de que ese repo es del alcance.

**Prohibido siempre**, aun con autorizacion: negacion de servicio / stress destructivo,
exfiltrar o exponer datos personales reales de terceros, pivoteo hacia redes fuera del
alcance, dejar backdoors o cambios persistentes, y probar sistemas de terceros. Ante
la duda de si algo esta en alcance: se DETIENE y se pregunta. Un pentest se acota, no
se improvisa.

## 1. Fases (PTES adaptado)

| Fase | Que se hace | Entregable |
|---|---|---|
| 1. Pre-engagement | RoE, alcance, autorizacion, ambiente objetivo, cuentas de prueba | `roe.md` firmado |
| 2. Reconocimiento | Superficie: rutas, endpoints (OpenAPI), subdominios propios, tecnologias, headers | `recon.md` |
| 3. Modelado de amenazas | Actores, activos, flujos de confianza, puntos de entrada, STRIDE por componente | `threat-model.md` |
| 4. Analisis de vulnerabilidades | SAST/SCA/secrets (appsec), config/infra (cloudsec), fuzzing dirigido (pentester) | hallazgos crudos |
| 5. Explotacion (solo autorizada) | Confirmar el hallazgo con un PoC minimo y NO destructivo | evidencia por hallazgo |
| 6. Post-explotacion | Alcance real del impacto SIN pivotear fuera del RoE ni tocar datos de terceros | impacto acotado |
| 7. Informe | Consolidar, puntuar (CVSS), priorizar, remediar | informe PDF + tickets |
| 8. Reprueba | Verificar cada fix con el mismo PoC (retest) | veredicto CERRADO/ABIERTO |

## 2. Cobertura por estandar (lo mas reciente)

- **OWASP Top 10 2021**: A01 Broken Access Control, A02 Cryptographic Failures, A03
  Injection, A04 Insecure Design, A05 Security Misconfiguration, A06 Vulnerable
  Components, A07 Identification/Authentication Failures, A08 Software/Data Integrity,
  A09 Logging/Monitoring Failures, A10 SSRF.
- **OWASP API Security Top 10 2023**: API1 BOLA (IDOR de objeto), API2 Broken
  Authentication, API3 Broken Object Property Level Authorization, API4 Unrestricted
  Resource Consumption, API5 Broken Function Level Authorization, API6 Unrestricted
  Access to Sensitive Business Flows, API7 SSRF, API8 Security Misconfiguration, API9
  Improper Inventory Management, API10 Unsafe Consumption of APIs.
- **OWASP WSTG** (Web Security Testing Guide) como catalogo de casos por area:
  identidad, autenticacion, autorizacion, sesion, validacion de entrada, errores,
  criptografia, logica de negocio, cliente.
- **OWASP MASVS/MASTG** si hay app movil; **OWASP ASVS** como baseline de verificacion.
- **CIS Benchmarks** y **Docker/Kubernetes CIS** para cloudsec (contenedor, host, CI/CD).

## 3. Checklist por clase (marca cada uno con evidencia o "no aplica")

**Control de acceso (A01 / BOLA / BFLA)** — el hallazgo mas comun y de mayor impacto:
- [ ] IDOR: cambiar un id de objeto en la URL/body accede a datos de otro usuario/tenant
- [ ] Escalada horizontal (otro usuario mismo rol) y vertical (rol superior)
- [ ] Fallback de autorizacion global en el arranque (no solo `[Authorize]` por controller)
- [ ] Endpoints administrativos accesibles con token de usuario normal
- [ ] Forzar flujo de negocio saltando pasos (aprobar sin autorizar, girar sin firmar)

**Autenticacion y sesion (A07 / API2)**:
- [ ] Rate limiting APLICADO (no solo declarado) en login, MFA, reset — probado con requests reales
- [ ] Lockout que cuente TAMBIEN fallos de MFA/2FA
- [ ] JWT: algoritmo seguro (rechaza `alg:none`), firma verificada, exp corto, sin `HS`/`RS` confundibles
- [ ] Sin fallback silencioso: si falta la clave de firma, el servicio ABORTA el arranque
- [ ] Flujos forzados sin bypass (cambio de contraseña obligatorio con guard real)
- [ ] Tokens/refresh no reutilizables tras logout; cookies `HttpOnly`/`Secure`/`SameSite`

**Inyeccion (A03)**: SQL/NoSQL, comandos, LDAP, plantillas (SSTI), deserializacion.
**SSRF (A10/API7)**: parametros de URL/webhook/import que el servidor consume.
**Cripto (A02)**: TLS, secretos en reposo, hashing de password (bcrypt/Argon2, nunca MD5/SHA1).
**Config (A05/API8)**: headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options,
Referrer-Policy), CORS sin wildcard en prod, errores sin stacktrace, debug apagado.
**Componentes (A06)**: `dotnet list package --vulnerable`, `npm audit`, `pip-audit`, imagenes base.
**Logica de negocio**: condiciones de carrera, manipulacion de montos/precios, replay.

## 4. Prueba de concepto (PoC) — regla de oro

Un hallazgo sin PoC reproducible es una SOSPECHA, no un hallazgo. Cada hallazgo confirmado
lleva:
- **Request exacto** (curl copy-paste) o pasos UI exactos (Playwright MCP) que lo disparan
- **Response/estado** que PRUEBA el impacto (dato ajeno visible, 200 donde debia 403, etc.)
- **Evidencia visual**: captura resaltada (`browser_highlight` + `browser_take_screenshot`)
  o respuesta capturada, numerada `00-`, `01-`...
- **Minimo y no destructivo**: se prueba lo SUFICIENTE para confirmar, jamas se borra,
  altera ni exfiltra data real. Un IDOR se prueba leyendo UN registro ajeno de prueba,
  no volcando la tabla.

## 5. Puntuacion y severidad (CVSS 3.1)

Cada hallazgo lleva un vector CVSS 3.1 y su score → severidad:
- **Critica** 9.0–10.0 · **Alta** 7.0–8.9 · **Media** 4.0–6.9 · **Baja** 0.1–3.9 · Info 0.0
Ajusta con el contexto de negocio (dato financiero, PII, alcance de tenants). El SLA de
remediacion: Critica inmediata · Alta 24-72h · Media al sprint · Baja al backlog.

## 6. Cadena de custodia de la evidencia

- Toda la evidencia vive en `.coordination/evidence/PENTEST-{id}/` (gitignored), nunca en
  ramas de codigo. Al tracker sube EMBEBIDA (rama `evidence` en GitHub / attachment+`<img>`
  en Azure), igual que QA.
- **Nunca** escribas secretos, credenciales, tokens de sesion capturados ni PII real en el
  informe, la wiki ni el chat: redactalos (`Bearer ***`, `rut: ***`). El informe prueba el
  hallazgo sin filtrar el dato.
- Registra fecha/hora, ambiente, version desplegada y cuenta usada por cada prueba.

## 7. Estructura del informe (resumen)

Resumen ejecutivo (para gerencia, sin jerga) → alcance y RoE → metodologia → tabla de
hallazgos por severidad → detalle por hallazgo (descripcion, impacto de negocio, PoC,
evidencia, CVSS, remediacion con ejemplo) → estado de reprueba → anexos. El detalle
completo del formato esta en `templates/pentest/` y lo arma `/dev-team:security-report`.

---
description: Revisa un Pull Request verificando codigo, tests, seguridad y cumplimiento de reglas del proyecto. Uso - /microservices-agents:review-pr $ARGUMENTS
---

Revisa el Pull Request: $ARGUMENTS

1. Si $ARGUMENTS es un numero o URL de PR, obtener los cambios con `gh pr diff $ARGUMENTS`
2. Si no hay argumento, revisar el PR del branch actual: `gh pr view`

Para cada archivo modificado, verificar:

### Codigo
- Sigue Clean Architecture? (Controllers → Services → Repositories)
- Usa DTOs? (no expone entidades)
- Validacion de input presente?
- Async/await en operaciones I/O?
- Sin string concatenation en SQL?
- Sin secrets hardcodeados?

### Tests
- Hay tests nuevos para funcionalidad nueva?
- Los tests existentes siguen pasando?

### Seguridad
- Input validado y sanitizado?
- Sin XSS, SQL injection, CSRF?
- Auth/authz correcto en endpoints nuevos?

### Git
- Commits siguen Conventional Commits?
- Solo archivos del area de responsabilidad del agente?
- Branch naming correcto?

### Formato
- Linter/formateador ejecutado?

Generar resumen:
- Cambios: N archivos, +X/-Y lineas
- Aprobado / Cambios requeridos / Bloqueado
- Lista de observaciones por categoria

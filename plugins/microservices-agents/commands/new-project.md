---
description: Crea un nuevo proyecto de microservicios a partir de un documento de requerimientos. Uso - /microservices-agents:new-project $ARGUMENTS
---

# Crear nuevo proyecto de microservicios

Recibiste un documento o descripcion de requerimientos: $ARGUMENTS

Ejecuta el siguiente flujo paso a paso:

## Paso 1: Leer y analizar requerimientos
- Si $ARGUMENTS es una ruta a un archivo (.docx, .pdf, .md, .txt), leelo completo
- Si es texto libre, usalo directamente como requerimientos
- Extrae: requerimientos funcionales, no funcionales, actores, flujos, integraciones

## Paso 2: Invocar al Arquitecto
Usa el agente `architect` para analizar los requerimientos y generar la propuesta de arquitectura.
El Arquitecto debe producir `architecture.md` con:
- Bounded contexts identificados
- Servicios propuestos (nombre, stack, BD, justificacion)
- API Gateway (tecnologia y justificacion)
- Frontend (SPA vs microfrontends)
- Comunicacion entre servicios
- Diagrama Mermaid
- Repos a crear
- Plan de ejecucion por fases

## Paso 3: Presentar propuesta al usuario
Muestra la propuesta completa y pregunta:
- "Aprobado" → continuar al paso 4
- Ajustes → el Arquitecto modifica y re-presenta

## Paso 4: Crear estructura del proyecto
Una vez aprobado:

1. Preguntar al usuario:
   - Nombre del proyecto (ej: ecommerce)
   - Directorio base (default: ~/projects/)
   - Crear repos en GitHub? (si → preguntar org; no → solo git init local)

2. Crear carpeta paraguas:
   ```
   {directorio}/{proyecto}/
   ├── .coordination/
   │   ├── handoffs/
   │   │   └── archive/
   │   ├── backlog.md
   │   ├── sprint-actual.md
   │   └── architecture.md
   ├── docker-compose.dev.yml
   └── .env.dev
   ```

3. Por cada repo del plan del Arquitecto, dentro de la carpeta paraguas:
   - `git init {proyecto}-{servicio}`
   - Crear estructura segun stack (Dockerfile, CI/CD, docker-compose.service.yml)
   - Generar CLAUDE.md con contexto del servicio
   - Generar .env.example
   - Crear README.md basico
   - `git add . && git commit -m "chore: initial scaffolding"`
   - Si el usuario eligio GitHub: `gh repo create {org}/{proyecto}-{servicio} --source . --push`

4. Generar docker-compose.dev.yml con todos los servicios

5. Generar backlog inicial en `.coordination/backlog.md` basado en las fases del Arquitecto

## Paso 5: Resumen final
Mostrar:
- Repos creados (locales y/o en GitHub)
- Estructura de la carpeta paraguas
- Proximos pasos: "Invoca al Lead con /microservices-agents:assign-task para comenzar a asignar trabajo"

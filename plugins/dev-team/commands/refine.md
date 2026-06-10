---
description: El Product Owner convierte tu pedido en Historias de Usuario profesionales (de negocio, con criterios de aceptacion Gherkin) y las crea en GitHub Projects o Azure DevOps Boards.
argument-hint: Que necesitas, en tus palabras (ej. "los analistas necesitan filtrar cobranzas por fecha") o ruta a un documento
---

# Refine: De pedido a Historias de Usuario

Pedido del usuario: $ARGUMENTS

Invoca al agente `product-owner` para ejecutar este flujo:

## Paso 1: Entender
- Si $ARGUMENTS es una ruta a documento (.docx, .pdf, .md, .txt), leerlo completo
- Si es texto libre, usarlo como punto de partida
- Si hay ambiguedades criticas: hacer MAXIMO 3 preguntas concretas al usuario

## Paso 2: Redactar las HUs
- HUs de NEGOCIO (valor para el usuario), nunca tecnicas
- Formato completo del PO: narrativa Como/Quiero/Para, contexto, criterios de
  aceptacion en Gherkin (verificables por QA), alcance, DoD, estimacion
- Dividir si es XL; detectar si ya existe una HU similar en el backlog (no duplicar)

## Paso 3: Presentar y aprobar
Mostrar las HUs al usuario ANTES de crearlas en el tracker. El usuario puede
ajustar prioridad, alcance o criterios.

## Paso 4: Crear en el tracker
Segun `tracker.provider` en `.coordination/config.json`:
- GitHub: `gh issue create` con labels + agregar al Project
- Azure: `az boards work-item create --type "Product Backlog Item"` con criterios de aceptacion
Actualizar `.coordination/backlog.md` con los IDs reales.

## Paso 5: Entregar al Lead
Handoff `po-to-lead-{fecha}.md` con las HUs listas y el orden recomendado.
Sugerir al usuario el siguiente paso: `/dev-team:assign-task` para asignarlas.

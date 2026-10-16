---
name: redaccion-negocio
description: Regla de oro de redaccion del equipo del Product Owner (po-team) - todo lo que se escribe (HUs, bugs, comentarios en el tracker, documentos, manuales, informes) en lenguaje funcional de negocio que entiende una persona no programadora, con titulos limpios sin codigos inventados, narrativa Como/Quiero/Para, criterios de aceptacion Gherkin verificables por la pantalla, alcance incluye/no incluye, formato de bug como lo vive el usuario, convencion opcional de prefijo de ambiente en bugs de Demo/Preprod, ejemplos buenos y malos y el test de lectura obligatorio. Cargala antes de redactar o revisar cualquier texto que vaya al tracker o a un documento.
---

# Redaccion de negocio (po-team)

El lector del PO **no es programador**: es QA, el cliente, la gerencia, la persona de la Mesa de
Servicios, el analista de negocio. Todo lo que el equipo del PO escribe — HUs, bugs, comentarios,
documentos, manuales, informes del tablero — se entiende a la primera lectura sin saber programar.
El COMO (pantallas internas, tablas, servicios, endpoints) lo decide el equipo de desarrollo y vive
en sus propias notas, nunca en la redaccion del PO.

## Prohibido en titulo y cuerpo principal
Endpoints, URLs internas, verbos HTTP, JSON, nombres de tablas o columnas, nombres de servicios,
clases, componentes o ramas, stacktraces, migraciones, versiones de librerias, jerga
("refactorizar", "deployar", "nullable", "parsear", "mergear", "hotfix", "payload", "front", "back").

## Permitido y bienvenido
Conceptos del negocio tal como los ve el usuario: "fecha de vencimiento", "monto maximo", "perfil
Ejecutivo", "operacion de factoring", "cesion", "nomina de confirming", nombres REALES de pantallas,
menus y botones ("boton Aprobar de la bandeja Operaciones pendientes"). Si un dato es necesario se
nombra como lo ve el usuario, no como se llama en la base de datos.

## Titulos limpios
Una frase de negocio clara y corta. Sin prefijos ni codigos inventados: el unico identificador es
el numero que pone el tracker.
- ❌ `[HU-042] [BACK-017] fix filtro cobranzas v2`
- ❌ `Agregar endpoint GET /operaciones?desde=`
- ✅ `Filtrar las operaciones por rango de fechas de vencimiento`
- ✅ (bug) `El listado de cesiones muestra operaciones de otro cliente`

**Excepcion configurable — prefijo de ambiente en bugs:** si `redaccion.prefijoAmbienteEnBugs` es
`true` en el config, un bug detectado en un ambiente Demo o Preprod lleva al inicio el nombre corto
del ambiente tal como esta en `ambientes.*.nombre` (ej. `DEMO CO - El resumen de la nomina no suma
el IVA`). Es la UNICA excepcion a titulos limpios, y el cuerpo igual especifica el ambiente exacto
(nombre + URL publica si aplica + fecha).

## Formato de Historia de Usuario
```markdown
**Como** {perfil o rol del negocio}
**Quiero** {lo que necesita hacer}
**Para** {el beneficio de negocio}

## Contexto
{Por que ahora, que problema resuelve, de donde viene (solicitud de la Mesa, cliente, normativa)}

## Criterios de aceptacion
1. **Dado** {situacion previa} **cuando** {accion del usuario} **entonces** {resultado que VE}
2. ...

## Alcance
- Incluye: ...
- No incluye: ...

## Ambientes y entrega
{Donde se validara: QA, Demo {pais}, Preprod {cliente}; quien da el VB}

## Estimacion
{puntos Fibonacci} — {justificacion en una linea de negocio}
```
Las notas tecnicas NO van en la HU. Si el equipo de desarrollo las necesita, viven en sus propios
items o comentarios separados.

## Criterios de aceptacion en Gherkin (reglas)
- Cada criterio se verifica **usando la pantalla como un usuario**, sin leer codigo ni la base.
- Uno por comportamiento; nada de "y ademas" con cinco cosas en un mismo criterio.
- Resultados observables: lo que aparece, lo que se habilita, el mensaje que se ve, el total que
  cuadra. Evitar "funciona correctamente", "se guarda bien", "es rapido".
- Incluir al menos un caso no feliz relevante (dato invalido, perfil sin permiso, monto excedido).
- Datos concretos de ejemplo cuando ayudan ("una operacion de 10.000.000 con vencimiento a 30 dias").
- ❌ `Dado que el servicio responde 200 cuando se llama al endpoint entonces el JSON trae el campo`
- ✅ `Dado una operacion aprobada por el Ejecutivo cuando el Jefe Comercial abre la bandeja
   entonces la operacion aparece con estado "Pendiente de su aprobacion"`

## Formato de bug (como lo vive el usuario)
```markdown
## Que pasa
{Que ve mal el usuario y a quien afecta}

## Ambiente
{nombre exacto del ambiente} · {fecha} · {perfil usado}

## Pasos para reproducirlo (como usuario)
1. Entrar a {pantalla real}
2. {accion}
3. ...

## Resultado esperado vs obtenido
- Esperado: {en terminos de negocio}
- Obtenido: {en terminos de negocio}

## Evidencia
{capturas embebidas — skill evidencia-po}

## Impacto
{Critico | Alto | Medio | Bajo} — {que proceso frena, a cuantos usuarios o clientes}
```
Lo tecnico (consola, red, request) jamas en el cuerpo: si existe, comentario aparte rotulado
"Anexo tecnico para desarrollo".

## Comentarios en el tracker
Mismo idioma: "Se valido en Demo CO el 14/10: cumple los criterios 1 y 2; el criterio 3 queda
observado porque el total no incluye el IVA (captura 03)". Nunca "se cayo el endpoint".

## Test de lectura (obligatorio antes de crear o actualizar cualquier item o documento)
1. ¿Una persona de negocio entiende QUE se pide y POR QUE sin preguntar nada?
2. ¿Hay alguna palabra de codigo o jerga en el titulo o el cuerpo principal?
3. ¿Cada criterio se puede verificar mirando la pantalla?
4. ¿El titulo es limpio (salvo el prefijo de ambiente configurado en bugs)?
Si falla cualquiera: REESCRIBIR antes de seguir.

## Trabajo tecnico que no es HU
Deuda, infraestructura o mejoras internas no son HU. Si el PO debe registrarlas, van como item
tecnico separado y su titulo dice el BENEFICIO ("Acelerar la carga del listado de operaciones"),
no la tecnica.

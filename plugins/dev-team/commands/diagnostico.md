---
description: Diagnostico del equipo en esta maquina - revisa que este todo lo necesario para trabajar (Node, Python, git, gh, navegador de pruebas), que los hooks del plugin arranquen, la carpeta del equipo y su configuracion, y los ultimos fallos registrados; dice en lenguaje claro que falta y lo arregla con tu OK. Usalo cuando el equipo no carga sus reglas, algo falla sin explicacion o despues de instalar o actualizar.
argument-hint: (sin argumentos) | detalle
---

> **Ejecucion INLINE obligatoria:** este es un COMANDO, no un agente. Ejecutalo en la sesion
> actual; nunca dentro de un subagente.

# Diagnostico

Pedido: $ARGUMENTS

1. Corre el diagnostico (solo lee, no cambia nada; sirve en cualquier terminal y sistema):

   ```
   node "${CLAUDE_PLUGIN_ROOT}/hooks/doctor.mjs"
   ```

   Si `node` no existe, ese es el problema: aplica el **Paso 0 — Entorno** de `/dev-team:start`
   (instalar Node.js y Python) y vuelve a correrlo.
2. **Cuentale el resultado a la persona en llano**, en pocas lineas: si el equipo puede
   trabajar o no, y por cada cosa que falte, que es y para que sirve (no pegues la salida
   tecnica salvo que pida `detalle`).
3. Por cada linea `FALTA`: ofrece arreglarlo tu (instalar lo que falte con el comando del
   sistema, corregir el archivo indicado) y hazlo con su OK. Por cada `AVISO`: explica el
   efecto y deja que decida.
4. Si hay **fallos de hooks** registrados, lee las ultimas entradas de
   `~/.faast-mcp/logs/hooks.log`, explica la causa en una frase y, si es un defecto del
   plugin (no de la maquina), dilo asi para que se reporte al mantenedor del marketplace.
5. Cierra con una sola linea: "el equipo puede trabajar" o lo que queda pendiente. Si se
   instalo algo, recuerda cerrar y volver a abrir la terminal y la sesion.

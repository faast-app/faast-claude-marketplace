# Rendimiento: lo que siente una persona y lo que aguanta una API

Dos preguntas distintas, dos mediciones distintas. Ninguna es una prueba de carga completa
(eso es un proyecto aparte, con infra): son **puertas baratas** que atrapan lo evidente.

## 1. Rendimiento percibido de una pantalla (qa-frontend)

Se mide en el navegador real con la plantilla `tests/perf` (`npm run test:perf`):

| Metrica | Que es para la persona | Presupuesto por defecto |
|---|---|---|
| **LCP** | Cuando aparece lo principal de la pantalla | ≤ 2500 ms |
| **CLS** | Cuanto "salta" el contenido mientras carga | ≤ 0.1 |
| **Peso** | Cuanto se descarga (importa en celular) | ≤ 1500 kB |
| **INP** | Cuanto tarda en responder un clic (solo si hay interaccion pesada) | ≤ 200 ms |

- Se mide contra el ambiente de pruebas, con datos realistas (una tabla con 3 filas no dice
  nada: usa el volumen de un cliente grande).
- **Dos corridas** dentro del presupuesto; si una falla, se reporta la peor.
- El JSON de la medicion (`web-vitals.json`) es la evidencia.
- Que reportar si falla: metrica, valor, presupuesto y **que se ve** ("la tabla aparece a los
  4.1 s; antes se ve la pagina en blanco"). La causa la busca frontend.

## 2. Humo de carga de una API (qa-backend)

Un endpoint R1 nuevo, o uno al que le cambiaron una consulta, se prueba con **pocos usuarios
durante poco tiempo** para ver si responde estable. Con k6 (si esta instalado):

```js
import http from 'k6/http';
import { check } from 'k6';
export const options = { vus: 10, duration: '30s', thresholds: { http_req_duration: ['p(95)<800'], http_req_failed: ['rate<0.01'] } };
export default function () {
  const r = http.get(`${__ENV.API_URL}/api/operaciones?page=1`, { headers: { Authorization: `Bearer ${__ENV.QA_TOKEN}` } });
  check(r, { '200': (x) => x.status === 200 });
}
```

- **Solo en un ambiente de pruebas** y con volumen acordado (10 usuarios, 30 s por defecto);
  nunca contra un ambiente compartido en horario de uso sin avisar, y jamas contra productivo.
- Umbral: p95 ≤ `qa.umbrales.apiP95Ms` (800 ms por defecto) y errores < 1 %.
- Sin k6: 30 requests secuenciales con `curl -w '%{time_total}'` y se reporta mediana y maximo,
  dejando claro que es una medicion debil.
- Señales que se reportan aunque pase: tiempo que crece con la pagina (falta indice o
  paginacion en servidor), tiempo que crece con usuarios (bloqueo), respuesta sin limite de
  tamaño.

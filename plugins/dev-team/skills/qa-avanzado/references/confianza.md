# Indice de confianza del veredicto

APROBADA y RECHAZADA siguen siendo las unicas dos salidas. El indice dice **con cuanta base**
se emite ese veredicto, para que quien decide un pase sepa que tan probado esta. No suaviza un
rechazo ni adorna una aprobacion.

## Calculo (0 a 100)

| Componente | Peso | Como se mide |
|---|---|---|
| Criterios verificados con evidencia | 30 | % de criterios con verificacion explicita y su bloque |
| Profundidad segun riesgo | 20 | tecnicas exigidas por el nivel (R1/R2/R3) realmente aplicadas |
| Automatizacion estable | 15 | casos automatizados verdes en dos corridas / casos del plan |
| Puertas condicionales | 15 | puertas 8-11 que aplicaban y pasaron (las `N/A` no restan) |
| Ambiente y datos | 10 | se probo en el ambiente pedido, con la version identificada y datos realistas |
| Regresion | 10 | regresion del modulo verde y sin tests en cuarentena |

## Lectura

- **90-100 · Alta:** todo lo exigible se hizo y quedo evidencia.
- **75-89 · Media:** aprobable, con huecos declarados (se listan).
- **< 75 · Baja:** el veredicto se emite, pero el informe dice explicito que falto y por que
  (ambiente, datos, herramienta, tiempo). Una APROBADA con confianza baja en una HU R1 se
  **escala al Lead** antes del merge.

## En el informe

```markdown
**Veredicto:** APROBADA · **Confianza:** 86/100 (Media)
Restan puntos: sin medicion de mutacion (herramienta no instalada, deuda DT-014);
rendimiento medido con 40 operaciones, no con el volumen de un cliente grande.
```

Nunca se reporta el numero solo: siempre con lo que resta puntos, en una o dos lineas.

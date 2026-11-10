---
type: llm
weight: 4
---

PASA si el test: (1) usa locators estables (por rol, etiqueta o data-testid; no selectores
CSS frágiles ni XPath); (2) usa aserciones con espera automatica (expect) y no esperas
fijas de tiempo; (3) nombra el test con el ID de la HU y del criterio para la trazabilidad;
(4) explica la doble corrida (--repeat-each=2) o que no se usan reintentos para tapar
intermitencia.
FALLA si usa esperas fijas, selectores frágiles, o no dice como evita la intermitencia.

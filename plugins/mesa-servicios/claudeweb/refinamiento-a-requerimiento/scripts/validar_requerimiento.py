#!/usr/bin/env python3
"""Valida consistencia y trazabilidad de un requerimiento FaaST.

Documentos:
  --spec       ESP_<Tema>_FaaST.md            (especificación funcional para desarrollo)
  --propuesta  Propuesta_<Tema>_<Cliente>.md  (visto bueno del solicitante)
  --matriz     imprime la matriz RN -> CA

Salida: ERRORES (bloquean "Listo para desarrollo") y AVISOS. Código 1 si hay errores.
"""
import argparse
import re
import sys
import unicodedata
from collections import defaultdict

GLOBAL_RE = re.compile(r"\b(RN|D|PR|CA|PT|IM)-(\d{2,})\b")
ESP_CODE_RE = re.compile(r"(?:PRY|CTZ|CC|BUG)-\d{4}-\d{3}|FaaST-ESP-[A-Z]{2,5}-\d{3}")
TABLE_ID_RE = re.compile(r"^\|\s*\**((?:RN|D|PR|CA|PT|IM)-\d+)\**\s*\|")

PLACEHOLDERS = [r"\bTBD\b", r"\bpor definir\b", r"\[completar\]", r"\bXXX\b",
                r"\[Tema\]", r"\[Cliente\]", r"\[DOM\]", r"\[NNN\]", r"\[rol\]",
                r"\[capacidad\]", r"AAAA-MM-DD"]

VAGOS = ["rápido", "rápidamente", "ágil", "eficiente", "en tiempo real", "fácil",
         "fácilmente", "intuitivo", "amigable", "adecuado", "adecuada", "apropiado",
         "apropiada", "según corresponda", "cuando aplique", "si es necesario",
         "etc.", "entre otros", "y similares", "normalmente", "generalmente",
         "habitualmente", "lo de siempre", "como ahora", "igual que antes",
         "debería", "podría", "algunos", "algunas", "varios", "varias"]

TECNICOS = ["tabla", "columna", "base de datos", "endpoint", "api", "backend",
            "frontend", "gateway", "microservicio", "repositorio", "repo", "query",
            "flag", "deploy", "null", "dto", "json", "payload", "servicio único"]

ADJUNTO_SIN_INTERPRETAR = [r"\bver (el )?(excel|adjunto|archivo|planilla|anexo)\b",
                           r"\bseg[úu]n (el )?(excel|adjunto|archivo|planilla)\b",
                           r"\bcomo (en|est[aá]) (el|la) (excel|planilla|adjunto)\b",
                           r"\b(la )?nueva f[óo]rmula\b(?!\s*[:=])", r"\bla f[óo]rmula (del|de la) (excel|planilla)\b"]
REFERENCIA_VAGA = [r"previamente (definid|establecid|acordad)", r"\bya (definid|establecid|acordad)",
                   r"\blo (establecido|vigente|definido|acordado)\b", r"seg[úu]n (lo )?(acordado|conversado|definido)",
                   r"como se (defini[óo]|acord[óo]|convers[óo])", r"\bprocedimiento habitual\b",
                   r"\b(que|como|donde) corresponda[n]?\b", r"\bdonde (aplique|sea necesario)\b",
                   r"seg[úu]n (la )?(normativa|pol[íi]tica)\b(?!\s+[A-ZÁÉÍÓÚ0-9])"]
SECCIONES_PROPUESTA = ["para qué es este documento", "lo que entendimos", "cómo funcionará",
                       "lo que queda fuera", "lo que necesitamos", "cómo sigue"]
SECCIONES_POR_TIPO = {
    "cambio menor": ["qué cambia exactamente", "dónde aplica", "cómo se verifica",
                     "lo que no incluye", "preguntas abiertas"],
    "cambio funcional": ["alcance en una mirada", "control de versiones", "objetivo y alcance",
                         "qué cambia exactamente", "reglas de negocio", "dónde aplica e impactos",
                         "criterios de aceptación", "activación y puesta en marcha",
                         "fuera de alcance", "trazabilidad de decisiones", "preguntas abiertas"],
    "reporte": ["alcance en una mirada", "control de versiones", "objetivo y alcance",
                "definición del reporte", "actores y permisos", "reglas de negocio",
                "criterios de aceptación", "fuera de alcance", "trazabilidad de decisiones",
                "preguntas abiertas"],
}
SECCIONES_SPEC = ["alcance en una mirada", "control de versiones", "objetivo y alcance", "resumen de la solución",
                  "qué cambia exactamente",
                  "actores y permisos", "flujo funcional", "reglas de negocio",
                  "pantallas y mensajes", "casos de borde", "dónde aplica e impactos", "criterios de aceptación",
                  "activación y puesta en marcha", "fuera de alcance",
                  "para resolver por desarrollo", "trazabilidad de decisiones",
                  "preguntas abiertas"]
DISENO_TECNICO = [r"\bCREATE\s+TABLE\b", r"\bALTER\s+TABLE\b", r"\b(GET|POST|PUT|PATCH|DELETE)\s+/",
                  r"\bapi/v\d", r"\.cs\b", r"\.tsx?\b", r"\bVARCHAR\b", r"^#+\s.*modelo de datos",
                  r"^#+\s.*contratos? de api", r"^#+\s.*impacto por repositorio", r"^#+\s.*tareas técnicas"]
ESTADOS = ["en refinamiento", "pendiente de aprobación", "listo para desarrollo"]


def norm(s):
    return unicodedata.normalize("NFC", s).lower()


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def sections(lines):
    cur, out = "", []
    for l in lines:
        if re.match(r"^#{1,3}\s", l):
            cur = norm(re.sub(r"^#+\s*(\d+(\.\d+)?\.?\s*)?", "", l).strip())
        out.append(cur)
    return out


def headings(lines):
    return [norm(re.sub(r"^#+\s*(\d+(\.\d+)?\.?\s*)?", "", l).strip())
            for l in lines if re.match(r"^#{1,3}\s", l)]


def strip_quotes(line):
    line = re.sub(r"\"[^\"]*\"|“[^”]*”|«[^»]*»|`[^`]*`", "", line)
    return re.sub(r"\[[TRAC] [^\]]*\]|\[U\]", "", line)


def meta(lines, key):
    """Lee '**Clave:** valor' o '| **Clave** | valor |'."""
    for l in lines:
        m = re.search(r"\*\*" + key + r":?\*\*:?\s*(.+?)(?:\s+·\s+\*\*|$)", l)
        if m and not l.startswith("|"):
            return m.group(1).strip()
        m = re.match(r"^\|\s*\**" + key + r"\**\s*\|\s*(.*?)\s*\|", l)
        if m:
            return m.group(1).strip()
    return None


def cells(l):
    return [c.strip() for c in l.strip().strip("|").split("|")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--propuesta")
    ap.add_argument("--matriz", action="store_true")
    a = ap.parse_args()

    err, warn = [], []
    spec = read(a.spec)
    ssec = sections(spec)

    # ---------- Definiciones
    defined, open_q = {}, []
    for i, l in enumerate(spec, 1):
        m = TABLE_ID_RE.match(l)
        if not m:
            continue
        idv = m.group(1)
        if not re.match(r"(RN|D|PR|CA|PT|IM)-\d{2,}$", idv):
            err.append(f"spec:{i} ID {idv} con formato inválido (dos dígitos mínimo)")
            continue
        if idv in defined:
            err.append(f"spec:{i} ID duplicado {idv} (también en línea {defined[idv]})")
        defined[idv] = i
        if idv.startswith("PR-") and "pregunta" in ssec[i - 1]:
            if "cerrad" not in norm(cells(l)[-1]):
                open_q.append(idv)

    for i, l in enumerate(spec, 1):
        if "pregunta" in ssec[i - 1] and l.startswith("|") and not TABLE_ID_RE.match(l) \
                and not re.match(r"^\|\s*-", l) and not re.match(r"^\|\s*(id|#|pregunta)\s*\|", norm(l)):
            if "cerrad" not in norm(cells(l)[-1]):
                open_q.append(f"línea {i}")

    code = ESP_CODE_RE.search("\n".join(spec))
    code = code.group(0) if code else None
    if not code:
        err.append("spec: no se encontró el correlativo `PRY-AAAA-NNN` (o CTZ/CC/BUG)")
    estado = norm(meta(spec, "Estado") or "")
    aprob = norm(meta(spec, "Aprobación") or "")
    tipo_raw = norm(meta(spec, "Tipo") or "")
    tipo = next((t for t in ["cambio menor", "cambio funcional", "reporte", "funcionalidad nueva"]
                 if t in tipo_raw and not ("|" in tipo_raw)), None)
    if not tipo:
        err.append(f"spec: tipo inválido o sin elegir '{tipo_raw}'. Usa uno de: Cambio menor, "
                   f"Cambio funcional, Reporte, Funcionalidad nueva")
        tipo = "funcionalidad nueva"
    menor = tipo == "cambio menor"
    requeridas = SECCIONES_POR_TIPO.get(tipo, SECCIONES_SPEC)

    ticket = norm(meta(spec, "Ticket de origen") or "")
    if not ticket or ticket.startswith("["):
        warn.append("spec: falta 'Ticket de origen' en el encabezado (ticket MDS o proyecto de implementación)")
    if not menor:
        estr = norm(meta(spec, "Estrategia") or "")
        if not estr or estr.startswith("[") or "·" in estr:
            warn.append("spec: falta la 'Estrategia' en Alcance en una mirada (modifica lo existente, "
                        "opción nueva que convive, extiende lo existente o nuevo sin equivalente)")
    asis = norm(meta(spec, "AS-IS de referencia") or "")
    if menor:
        asis = "no aplica"
    if not asis or asis.startswith("["):
        err.append("spec: falta 'AS-IS de referencia' en el encabezado (fuente, 'No disponible' o 'No aplica')")
    if not menor and (not norm(meta(spec, "Otros insumos") or "") or norm(meta(spec, "Otros insumos") or "").startswith("[")):
        warn.append("spec: falta 'Otros insumos' en el encabezado (lo usado o 'Ninguno')")
    if asis and "no disponible" in asis:
        warn.append("spec: elaborada sin AS-IS; desarrollo debe validar los supuestos sobre el comportamiento actual")


    sh = headings(spec)
    for sec in requeridas:
        if not any(sec in h for h in sh):
            err.append(f"spec: falta la sección '{sec}' (requerida para {tipo})")
    if tipo in ("cambio funcional", "funcionalidad nueva"):
        act = "\n".join(l for l, s_ in zip(spec, ssec) if "activación" in s_)
        if "desactivad" not in norm(act) or "tenant" not in norm(act):
            warn.append("spec: activación no declara 'desactivada por defecto' y valores por tenant")

    # ---------- Reglas con origen y cobertura por criterios
    rn_ids = sorted(k for k in defined if k.startswith("RN-"))
    ca_ids = sorted(k for k in defined if k.startswith("CA-"))
    cobertura = defaultdict(list)
    for i, l in enumerate(spec, 1):
        m = TABLE_ID_RE.match(l)
        if not m:
            continue
        idv, c = m.group(1), cells(l)
        if idv.startswith("RN-"):
            ult = norm(c[-1])
            if not re.search(r"\bD-\d{2,}", c[-1]) and not re.search(r"\[[trac] |\[u\]", ult):
                err.append(f"spec:{i} {idv} sin origen (D-xx o evidencia [T …]/[R …]/[A …]/[C …]/[U])")
        if idv.startswith("CA-"):
            rns = re.findall(r"\bRN-\d{2,}\b", c[-1]) if len(c) >= 3 else []
            ims = re.findall(r"\bIM-\d{2,}\b", c[-1]) if len(c) >= 3 else []
            if not rns and not ims:
                err.append(f"spec:{i} {idv} sin regla ni lugar en la columna Ref.")
            for r in rns:
                cobertura[r].append(idv)
    for r in rn_ids:
        if not cobertura.get(r):
            err.append(f"spec:{defined[r]} {r} no está verificada por ningún criterio de aceptación")
    if not ca_ids and not menor:
        err.append("spec: sin criterios de aceptación CA-xx")
    if menor:
        verif = [l for l, s_ in zip(spec, ssec) if "cómo se verifica" in s_ and l.strip().startswith("- [")]
        if not verif:
            err.append("ficha: 'Cómo se verifica' sin verificaciones (- [ ] …)")
        donde = [l for l, s_ in zip(spec, ssec) if s_.startswith("dónde aplica") and l.startswith("|")
                 and not re.match(r"^\|\s*-", l) and "¿cambia?" not in norm(l)]
        if not donde:
            err.append("ficha: 'Dónde aplica' sin lugares")

    # ---------- Diseño técnico colado
    for i, l in enumerate(spec, 1):
        for pat in DISENO_TECNICO:
            if re.search(pat, l, re.IGNORECASE):
                warn.append(f"spec:{i} parece diseño técnico (le corresponde a desarrollo): {l.strip()[:70]}")
                break

    # ---------- Referencias inexistentes
    docs = [("spec", a.spec, spec)]
    if a.propuesta:
        prop = read(a.propuesta)
        docs.append(("propuesta", a.propuesta, prop))
    for i, l in enumerate(spec, 1):
        for x, y in GLOBAL_RE.findall(l):
            if f"{x}-{y}" not in defined:
                err.append(f"spec:{i} referencia a {x}-{y}, que no está definido")

    # ---------- Ficha de cambio menor: la lee el solicitante, sin jerga técnica
    if menor:
        for i, l in enumerate(spec, 1):
            limpio = norm(strip_quotes(l))
            for t in TECNICOS:
                if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", limpio):
                    warn.append(f"ficha:{i} término técnico '{t}' (la ficha la aprueba el solicitante): {l.strip()[:70]}")

    # ---------- Propuesta
    if a.propuesta:
        ph = headings(prop)
        for sec in SECCIONES_PROPUESTA:
            if not any(sec in h for h in ph):
                warn.append(f"propuesta: falta la sección '{sec}'")
        for i, l in enumerate(prop, 1):
            if re.search(r"\b(RN|D|PR|CA|PT)-\d+", l):
                err.append(f"propuesta:{i} ID interno en documento para el solicitante: {l.strip()[:70]}")
            limpio = norm(strip_quotes(l))
            for t in TECNICOS:
                if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", limpio):
                    warn.append(f"propuesta:{i} término técnico '{t}': {l.strip()[:70]}")

    # ---------- Estado
    marcados = [e for e in ESTADOS if e in estado]
    if len(marcados) != 1:
        err.append(f"spec: estado inválido '{estado}'. Usa uno de: {', '.join(ESTADOS)}")
    else:
        e = marcados[0]
        if open_q and e != "en refinamiento":
            err.append(f"Estado '{e}' con preguntas abiertas: {', '.join(open_q)}")
        elif open_q:
            warn.append(f"Preguntas abiertas (NO está listo): {', '.join(open_q)}")
        if e == "listo para desarrollo" and (not aprob.startswith("aprobado") or "observaciones" in aprob):
            err.append(f"'Listo para desarrollo' sin visto bueno del solicitante (Aprobación: '{aprob}'). "
                       f"Sin visto bueno no hay issue de backlog")
        elif e == "listo para desarrollo" and not re.search(r"(propuesta|ficha)\s*v\d", aprob):
            warn.append("Aprobación sin la versión de la propuesta aprobada (ej. 'propuesta v1.1')")
        if e != "en refinamiento" and not a.propuesta and not menor:
            warn.append("Validar también la propuesta funcional (--propuesta)")

    # ---------- Cobertura de lugares e impactos (IM-xx) por criterios
    im_ids = sorted(k for k in defined if k.startswith("IM-"))
    im_cobertura = defaultdict(list)
    for i, l in enumerate(spec, 1):
        m = TABLE_ID_RE.match(l)
        if m and m.group(1).startswith("CA-"):
            for x in re.findall(r"\bIM-\d{2,}\b", cells(l)[-1]):
                im_cobertura[x].append(m.group(1))
    for imid in im_ids:
        c = [norm(x) for x in cells(spec[defined[imid] - 1])]
        if "no" in c or any(x.startswith("no:") or x.startswith("no ") for x in c[2:5]):
            continue
        if not im_cobertura.get(imid):
            err.append(f"spec:{defined[imid]} {imid} (lugar o impacto que cambia) sin criterio de aceptación que lo verifique")
    if not im_ids and tipo in ("cambio funcional", "funcionalidad nueva"):
        warn.append("spec: sin matriz 'Dónde aplica' (IM-xx). Todo cambio vive en al menos un lugar")

    # ---------- Referencias vagas (ambos documentos)
    for name, path, lines in docs:
        for i, l in enumerate(lines, 1):
            limpio = norm(strip_quotes(l))
            if re.search(r"\bD-\d{2,}|\[[ac] |\bIM-\d{2,}", norm(l)):
                continue
            for pat in REFERENCIA_VAGA:
                if re.search(pat, limpio):
                    err.append(f"{path}:{i} referencia vaga sin resolver (decir qué es y escribir su contenido): "
                               f"{l.strip()[:70]}")
                    break

    # ---------- Adjuntos sin interpretar (ambos documentos)
    for name, path, lines in docs:
        for i, l in enumerate(lines, 1):
            limpio = norm(strip_quotes(l))
            for pat in ADJUNTO_SIN_INTERPRETAR:
                if re.search(pat, limpio):
                    err.append(f"{path}:{i} remite a un adjunto o a 'la nueva fórmula' sin escribirla: "
                               f"{l.strip()[:70]}")
                    break

    # ---------- Marcadores y términos vagos
    for name, path, lines in docs:
        for i, l in enumerate(lines, 1):
            for pat in PLACEHOLDERS:
                if re.search(pat, l, re.IGNORECASE):
                    err.append(f"{path}:{i} marcador sin completar: {l.strip()[:70]}")
                    break
            limpio = norm(strip_quotes(l))
            for v in VAGOS:
                if re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", limpio):
                    warn.append(f"{path}:{i} término vago '{v}': {l.strip()[:70]}")

    # ---------- Reporte
    print(f"{code or 'ESP sin código'} · {tipo} · {len(rn_ids)} RN · {len(ca_ids)} CA · "
          f"{sum(k.startswith('D-') for k in defined)} decisiones · "
          f"{sum(k.startswith('IM-') for k in defined)} lugares/impactos · "
          f"{sum(k.startswith('PT-') for k in defined)} puntos técnicos · estado: {estado or '—'}")
    for e in err:
        print("ERROR  ", e)
    for w in warn:
        print("AVISO  ", w)
    if not err:
        print("OK: sin errores de consistencia ni trazabilidad.")
    if a.matriz:
        print("\n| Regla | Verificada por |\n|---|---|")
        for r in rn_ids:
            print(f"| {r} | {', '.join(cobertura.get(r, [])) or '—'} |")
        for r in sorted(k for k in defined if k.startswith("IM-")):
            print(f"| {r} | {', '.join(im_cobertura.get(r, [])) or '—'} |")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()

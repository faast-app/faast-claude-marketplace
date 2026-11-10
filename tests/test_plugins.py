"""Pruebas de los hooks y scripts de los equipos. Sin dependencias: `python -m unittest discover tests`.

Corren en Windows, macOS y Linux (CI). Cada prueba arma un proyecto temporal con la carpeta
del equipo FUERA de un repo git, como exige el plugin, y ejecuta los hooks igual que lo hace
Claude Code: `node hooks/run.mjs <script>` con el payload por stdin.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EQUIPOS = {
    "dev-team": {"carpeta": ".coordination", "agente": "dba", "lead": "lead"},
    "mesa-servicios": {"carpeta": ".mesa", "agente": "analista", "lead": "mesa-lead"},
    "po-team": {"carpeta": ".po-team", "agente": "refinador", "lead": "po-lead"},
    "marketing": {"carpeta": ".marketing", "agente": "director-motion", "lead": "director-marketing"},
}


def hooks(plugin):
    return os.path.join(RAIZ, "plugins", plugin, "hooks")


class Proyecto:
    """Carpeta de proyecto temporal: <tmp>/<carpeta del equipo>/config.json y <tmp>/repo (git)."""

    def __init__(self, carpeta, config=None):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="faast-test-"))
        self.equipo = os.path.join(self.tmp, carpeta)
        self.repo = os.path.join(self.tmp, "repo")
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.equipo)
        os.makedirs(self.repo)
        os.makedirs(self.home)
        with open(os.path.join(self.equipo, "config.json"), "w", encoding="utf-8") as f:
            json.dump(config or {"ambientes": {"demo": {"clase": "pruebas"}}}, f)
        subprocess.run(["git", "init", "-q", self.repo], check=True)

    def entorno(self):
        env = dict(os.environ, HOME=self.home, USERPROFILE=self.home, CLAUDE_PROJECT_DIR=self.repo)
        env.pop("FAAST_PYTHON", None)
        return env

    def borrar(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


def correr_hook(plugin, script, payload, proyecto, extra=()):
    entrada = json.dumps(payload) if payload is not None else ""
    r = subprocess.run(["node", os.path.join(hooks(plugin), "run.mjs"), script, *extra],
                       input=entrada.encode("utf-8"), capture_output=True, env=proyecto.entorno(),
                       cwd=proyecto.repo, timeout=60)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def correr_py(ruta, args, proyecto, entrada=None):
    r = subprocess.run([sys.executable, ruta, *args], input=entrada, capture_output=True, text=True,
                       encoding="utf-8", env=proyecto.entorno(), cwd=proyecto.repo, timeout=60)
    return r.returncode, r.stdout, r.stderr


class HooksDeLosCuatroEquipos(unittest.TestCase):
    def setUp(self):
        self.proyectos = {p: Proyecto(d["carpeta"]) for p, d in EQUIPOS.items()}

    def tearDown(self):
        for pr in self.proyectos.values():
            pr.borrar()

    def test_protocolo_de_sesion_carga_y_trae_las_reglas(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                rc, out, _ = correr_hook(plugin, "session_context.py", None, pr, ["--avisar"])
                self.assertEqual(rc, 0)
                self.assertIn("COMO LE HABLAS AL USUARIO", out)
                self.assertIn("CANAL, ROLES Y PERMISOS", out)
                self.assertIn(pr.equipo, out, "debe imprimir la ruta absoluta de la carpeta del equipo")

    def test_inicio_de_agente_inyecta_contexto_json_valido(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                payload = {"hook_event_name": "SubagentStart", "agent_type": f"{plugin}:{EQUIPOS[plugin]['agente']}",
                           "cwd": pr.repo, "task": "tarea de prueba"}
                rc, out, _ = correr_hook(plugin, "log-activity.py", payload, pr, ["@project"])
                self.assertEqual(rc, 0)
                ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
                self.assertIn(pr.equipo, ctx)
                self.assertIn("NUNCA pidas que te escriba en tu hilo", ctx)
                self.assertIn("pedidos_usuario.py", ctx)
                actividad = os.path.join(pr.equipo, "metrics", "activity.jsonl")
                self.assertTrue(os.path.exists(actividad), "debe registrar task_start")
                self.assertEqual(json.loads(open(actividad, encoding="utf-8").readline())["event"], "task_start")

    def test_agente_de_otro_plugin_no_se_registra(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                rc, out, _ = correr_hook(plugin, "log-activity.py",
                                         {"hook_event_name": "SubagentStart", "agent_type": "otro:desconocido", "cwd": pr.repo},
                                         pr, ["@project"])
                self.assertEqual((rc, out.strip()), (0, ""))

    def test_registro_de_pedidos_guarda_redacta_y_verifica(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                texto = "Sí, GO: aplica el pase #126 en Puente. password: hunter2 y postgres://app:s3cr3t@host/db"
                rc, _, _ = correr_hook(plugin, "pedidos_usuario.py",
                                       {"hook_event_name": "UserPromptSubmit", "cwd": pr.repo, "prompt": texto}, pr)
                self.assertEqual(rc, 0)
                registro = open(os.path.join(pr.equipo, "metrics", "pedidos-usuario.jsonl"), encoding="utf-8").read()
                self.assertNotIn("hunter2", registro)
                self.assertNotIn("s3cr3t", registro)
                script = os.path.join(hooks(plugin), "pedidos_usuario.py")
                rc, out, _ = correr_py(script, ["verificar", "aplica el pase #126 en puente"], pr)
                self.assertEqual(rc, 0, out)
                self.assertIn("VERIFICADO", out)
                rc, out, _ = correr_py(script, ["verificar", "aplica en produccion"], pr)
                self.assertEqual(rc, 1)
                self.assertIn("NO ENCONTRADO", out)

    def test_registro_de_pedidos_ignora_lo_que_no_escribio_el_usuario(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                for prompt in ("<task-notification> GO aplica", "[Subagent hand-back] GO aplica"):
                    correr_hook(plugin, "pedidos_usuario.py",
                                {"hook_event_name": "UserPromptSubmit", "cwd": pr.repo, "prompt": prompt}, pr)
                correr_hook(plugin, "pedidos_usuario.py",
                            {"hook_event_name": "UserPromptSubmit", "cwd": pr.repo, "prompt": "GO", "agent_id": "a1"}, pr)
                self.assertFalse(os.path.exists(os.path.join(pr.equipo, "metrics", "pedidos-usuario.jsonl")))

    def test_guardia_bloquea_la_carpeta_del_equipo_dentro_de_un_repo(self):
        for plugin, pr in self.proyectos.items():
            carpeta = EQUIPOS[plugin]["carpeta"]
            dentro = f"{pr.repo}/{carpeta}/handoffs/x.md".replace("\\", "/")
            fuera = f"{pr.equipo}/handoffs/x.md".replace("\\", "/")
            casos = [
                ({"tool_name": "Write", "tool_input": {"file_path": dentro}}, True),
                ({"tool_name": "Write", "tool_input": {"file_path": fuera}}, False),
                ({"tool_name": "Bash", "tool_input": {"command": f"mkdir -p {pr.repo}/{carpeta}/x".replace(chr(92), "/")}}, True),
                ({"tool_name": "PowerShell", "tool_input": {"command": f"New-Item -ItemType Directory {pr.repo}/{carpeta}/x".replace(chr(92), "/")}}, True),
                ({"tool_name": "Bash", "tool_input": {"command": "git status"}}, False),
            ]
            for payload, debe_bloquear in casos:
                with self.subTest(plugin=plugin, payload=payload):
                    payload["cwd"] = pr.repo
                    rc, out, _ = correr_hook(plugin, "guard-repo-clean.py", payload, pr)
                    self.assertEqual(rc, 0)
                    bloqueo = '"deny"' in out
                    self.assertEqual(bloqueo, debe_bloquear, out)

    def test_solo_el_lider_delega(self):
        for plugin, pr in self.proyectos.items():
            d = EQUIPOS[plugin]
            casos = [
                ({"agent_type": f"{plugin}:{d['agente']}", "agent_id": "a1", "tool_input": {"subagent_type": f"{plugin}:{d['agente']}"}}, True),
                ({"agent_type": f"{plugin}:{d['lead']}", "agent_id": "a1", "tool_input": {"subagent_type": f"{plugin}:{d['agente']}"}}, False),
                ({"tool_input": {"subagent_type": f"{plugin}:{d['agente']}"}}, False),  # sesion principal
            ]
            for payload, debe_bloquear in casos:
                with self.subTest(plugin=plugin, payload=payload):
                    payload.update({"hook_event_name": "PreToolUse", "tool_name": "Agent", "cwd": pr.repo})
                    rc, out, _ = correr_hook(plugin, "block-nested-delegation.py", payload, pr)
                    self.assertEqual(rc, 0)
                    self.assertEqual('"deny"' in out, debe_bloquear, out)

    def test_un_hook_que_falla_no_rompe_la_sesion_y_deja_rastro(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                r = subprocess.run(["node", os.path.join(hooks(plugin), "run.mjs"), "block-nested-delegation.py"],
                                   input=b"esto no es json", capture_output=True, env=pr.entorno(), cwd=pr.repo, timeout=60)
                self.assertEqual(r.returncode, 0)
                self.assertEqual(r.stdout, b"")
                registro = os.path.join(pr.home, ".faast-mcp", "logs", "hooks.log")
                self.assertTrue(os.path.exists(registro), "el fallo debe quedar en el registro")
                self.assertEqual(json.loads(open(registro, encoding="utf-8").readline())["plugin"], plugin)

    def test_script_inexistente_no_falla(self):
        pr = self.proyectos["dev-team"]
        rc, out, _ = correr_hook("dev-team", "no-existe.py", {}, pr)
        self.assertEqual((rc, out), (0, ""))

    def test_diagnostico(self):
        for plugin, pr in self.proyectos.items():
            with self.subTest(plugin=plugin):
                r = subprocess.run(["node", os.path.join(hooks(plugin), "doctor.mjs"), "--proyecto", pr.repo, "--json"],
                                   capture_output=True, env=pr.entorno(), cwd=pr.repo, timeout=120)
                d = json.loads(r.stdout.decode("utf-8"))
                self.assertEqual(d["plugin"], plugin)
                estados = {f["nombre"]: f["estado"] for f in d["filas"]}
                self.assertEqual(estados["Python 3"], "OK")
                self.assertEqual(estados["Archivos de los hooks"], "OK")
                self.assertEqual(estados["Arranque del protocolo de sesion"], "OK")
                self.assertEqual(estados["config.json"], "OK")

    def test_python_universal(self):
        r = subprocess.run(["node", os.path.join(hooks("dev-team"), "py.mjs"), "-c", "print('ñandú ok')"],
                           capture_output=True, timeout=60)
        self.assertEqual(r.returncode, 0)
        self.assertIn("ñandú ok", r.stdout.decode("utf-8"))


class MemoriaDelEquipo(unittest.TestCase):
    MEM = os.path.join(RAIZ, "plugins", "dev-team", "skills", "memoria-equipo", "scripts", "memoria.py")

    def setUp(self):
        self.pr = Proyecto(".coordination")
        os.makedirs(os.path.join(self.pr.equipo, "wiki", "decisiones"))
        with open(os.path.join(self.pr.equipo, "wiki", "decisiones", "adr-003.md"), "w", encoding="utf-8") as f:
            f.write("# ADR-003 Tablas de operaciones\n\n## Decision\nLas tablas de operaciones paginan en servidor con 10 filas.\n")

    def tearDown(self):
        self.pr.borrar()

    def mem(self, *args):
        return correr_py(self.MEM, [*args, "--coord", self.pr.equipo], self.pr)

    def test_ciclo_aprender_buscar_feedback_consolidar(self):
        rc, out, _ = self.mem("aprender", "--tipo", "diseno", "--agente", "ui-designer", "--fuente", "usuario", "--texto",
                              "El usuario eligio la tabla como protagonista con densidad compacta; rechazo tarjetas grandes")
        self.assertIn("APRENDIDA", out)
        lid = out.split()[1]
        rc, out, _ = self.mem("aprender", "--tipo", "diseno", "--texto",
                              "El usuario eligió la tabla como protagonista, densidad compacta; rechazó las tarjetas grandes")
        self.assertIn("REFORZADA", out, "una leccion casi igual refuerza, no duplica")
        rc, out, _ = self.mem("buscar", "tabla de operaciones compacta")
        self.assertIn(lid, out)
        self.assertIn("adr-003.md", out, "tambien recupera de la wiki")
        rc, out, _ = self.mem("feedback", lid, "util")
        self.assertIn("util=1", out)
        rc, out, _ = self.mem("evaluar")
        self.assertIn("recall@5 = 100%", out)
        rc, out, _ = self.mem("para-agente", "ui-designer", "--tarea", "pantalla de operaciones")
        self.assertIn(lid, out)
        rc, out, _ = self.mem("consolidar")
        self.assertEqual(rc, 0)
        manual = os.path.join(self.pr.equipo, "memoria", "aprendizajes", "ui-designer.md")
        self.assertIn("tabla como protagonista", open(manual, encoding="utf-8").read())

    def test_leccion_rechazada_tres_veces_se_retira(self):
        _, out, _ = self.mem("aprender", "--tipo", "bd", "--texto", "En Puente los scripts se corren dos veces siempre")
        lid = out.split()[1]
        for _ in range(3):
            _, out, _ = self.mem("feedback", lid, "no-util")
        self.assertIn("estado=retirada", out)
        _, out, _ = self.mem("buscar", "scripts puente dos veces", "--solo", "lecciones")
        self.assertNotIn(lid, out)

    def test_rechaza_leccion_sin_tipo_valido(self):
        rc, _, errtxt = self.mem("aprender", "--tipo", "inventado", "--texto", "algo suficientemente largo para pasar")
        self.assertEqual(rc, 2)


class HerenciaDeLaLibreria(unittest.TestCase):
    KIT = os.path.join(RAIZ, "plugins", "dev-team", "skills", "libreria-faast", "scripts", "kit_libreria.py")

    def setUp(self):
        self.pr = Proyecto(".coordination")
        self.kit = os.path.join(self.pr.equipo, "design", "DSN-001", "faast-kit")
        os.makedirs(self.kit)
        with open(os.path.join(self.kit, "faast-kit.css"), "w", encoding="utf-8") as f:
            f.write("/* @faast-app/ui 0.8.0 - faast-kit.css (generated, do not edit). */\n"
                    ":root{--faast-text-primary:#151515;--faast-space-4:1rem;--faast-font-sans:Inter}\n"
                    ".faast-button{color:var(--faast-text-primary)}.faast-button--primary{}\n")
        with open(os.path.join(self.kit, "markup.json"), "w", encoding="utf-8") as f:
            json.dump({"examples": [{"id": "button", "html": "<button class=\"faast-button faast-button--md\">x</button>"}]}, f)
        self.ui = os.path.join(self.pr.equipo, "design", "DSN-001", "02-ui")
        os.makedirs(self.ui)

    def tearDown(self):
        self.pr.borrar()

    def pagina(self, nombre, estilo, cuerpo):
        ruta = os.path.join(self.ui, nombre)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f'<html lang="es"><head><link rel="stylesheet" href="../faast-kit/faast-kit.css">'
                    f"<style>{estilo}</style></head><body>{cuerpo}</body></html>")
        return ruta

    def test_propuesta_que_hereda_pasa(self):
        buena = self.pagina("buena.html", ".dsn-x{padding:var(--faast-space-4);color:var(--faast-text-primary)}",
                            '<button class="faast-button faast-button--md dsn-x">Guardar Cambios</button>')
        rc, out, _ = correr_py(self.KIT, ["verificar", buena, "--kit", self.kit], self.pr)
        self.assertEqual(rc, 0, out)
        self.assertIn("HERENCIA: PASA", out)

    def test_propuesta_que_inventa_falla_con_cada_motivo(self):
        mala = self.pagina("mala.html",
                           ".x{color:#7c3aed;font-family:Poppins} .faast-button{border-radius:20px} :root{--faast-text-primary:#f0f} .y{margin:var(--faast-nope)}",
                           '<button class="faast-btn x">Hola</button>')
        rc, out, _ = correr_py(self.KIT, ["verificar", mala, "--kit", self.kit, "--json"], self.pr)
        self.assertEqual(rc, 1)
        codigos = {e["codigo"] for e in json.loads(out)["resultados"][0]["errores"]}
        self.assertTrue({"color-literal", "fuente-literal", "clase-inventada", "clase-redefinida",
                         "variable-inexistente", "variable-pisada"} <= codigos, codigos)

    def test_incrustar_deja_un_solo_archivo(self):
        buena = self.pagina("b.html", "", '<button class="faast-button">x</button>')
        rc, out, _ = correr_py(self.KIT, ["incrustar", buena, "--kit", self.kit], self.pr)
        self.assertEqual(rc, 0, out)
        unico = open(os.path.join(self.ui, "b.autocontenido.html"), encoding="utf-8").read()
        self.assertNotIn('rel="stylesheet"', unico)
        self.assertIn("--faast-text-primary", unico)


class Permisos(unittest.TestCase):
    def test_proponer_no_escribe_y_aplicar_fusiona_sin_tocar_deny(self):
        pr = Proyecto(".coordination", {"ambientes": {"demo": {"clase": "pruebas"}, "prod": {"clase": "productivo"}}})
        try:
            script = os.path.join(hooks("dev-team"), "permisos_equipo.py")
            ajustes = os.path.join(pr.repo, ".claude", "settings.local.json")
            rc, out, _ = correr_py(script, ["proponer", "--proyecto", pr.repo], pr)
            self.assertEqual(rc, 0)
            self.assertFalse(os.path.exists(ajustes), "proponer no debe escribir")
            self.assertIn("Ambientes de PRUEBAS de este proyecto: demo", out)
            self.assertIn("Ambientes PRODUCTIVOS de este proyecto: prod", out)
            os.makedirs(os.path.dirname(ajustes))
            with open(ajustes, "w", encoding="utf-8") as f:
                json.dump({"permissions": {"deny": ["Bash(git log *)"], "allow": ["Bash(mi regla)"]}}, f)
            correr_py(script, ["aplicar", "--proyecto", pr.repo], pr)
            p = json.load(open(ajustes, encoding="utf-8"))["permissions"]
            self.assertIn("Bash(mi regla)", p["allow"])
            self.assertIn("Bash(git status *)", p["allow"])
            self.assertNotIn("Bash(git log *)", p["allow"], "una regla en deny no pasa a allow")
            self.assertIn("Bash(git push *)", p["ask"])
            self.assertFalse(any("*)" == r[-2:] and r in ("Bash(*)",) for r in p["allow"]), "nunca reglas amplias")
        finally:
            pr.borrar()


class EvidenciaDelPO(unittest.TestCase):
    def test_sube_a_la_rama_de_evidencia_sin_tocar_la_de_trabajo(self):
        pr = Proyecto(".po-team")
        try:
            remoto = os.path.join(pr.tmp, "remoto.git")
            clon = os.path.join(pr.tmp, "clon")
            origen = os.path.join(pr.tmp, "origen")
            os.makedirs(origen)
            g = lambda *a, cwd=None: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *a],
                                                    cwd=cwd, check=True, capture_output=True)
            g("init", "-q", "--bare", remoto)
            g("clone", "-q", remoto, clon)
            g("commit", "-q", "--allow-empty", "-m", "init", cwd=clon)
            g("push", "-q", "origin", "HEAD", cwd=clon)
            g("config", "user.name", "t", cwd=clon)
            g("config", "user.email", "t@example.com", cwd=clon)
            rama = subprocess.run(["git", "branch", "--show-current"], cwd=clon, capture_output=True, text=True).stdout.strip()
            open(os.path.join(origen, "captura.png"), "w").write("x")
            open(os.path.join(origen, "notas.txt"), "w").write("no se sube")
            script = os.path.join(RAIZ, "plugins", "po-team", "skills", "evidencia-po", "scripts", "subir_evidencia.py")
            rc, out, errtxt = correr_py(script, ["--clon", clon, "--destino", "evidence/po/1-x/v1", "--origen", origen,
                                                 "--mensaje", "evidence(po): #1"], pr)
            self.assertEqual(rc, 0, out + errtxt)
            archivos = subprocess.run(["git", "ls-tree", "-r", "--name-only", "evidence"], cwd=remoto,
                                      capture_output=True, text=True).stdout.split()
            self.assertIn("evidence/po/1-x/v1/captura.png", archivos)
            self.assertNotIn("evidence/po/1-x/v1/notas.txt", archivos)
            actual = subprocess.run(["git", "branch", "--show-current"], cwd=clon, capture_output=True, text=True).stdout.strip()
            self.assertEqual(actual, rama, "la rama de trabajo no cambia")
            rc, _, _ = correr_py(script, ["--clon", clon, "--destino", "../fuera", "--origen", origen, "--mensaje", "x"], pr)
            self.assertEqual(rc, 1, "un destino con .. se rechaza")
        finally:
            pr.borrar()


class Repositorio(unittest.TestCase):
    def test_validador_estructural_pasa(self):
        r = subprocess.run([sys.executable, os.path.join(RAIZ, "tools", "validar.py")], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

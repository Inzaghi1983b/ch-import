import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap

"""Offline-Tests des Agent-Gates (.github/workflows/agent-gate.yml) mit einem Fake-gh.

Aufruf: python .github/gate-tests/test_gate.py [pfad/zu/agent-gate.yml]
Exit-Code 0 nur, wenn alle Faelle wie erwartet ausfallen (CI-Schritt). Fuehrt kein echtes gh aus.
"""

here = os.path.dirname(os.path.abspath(__file__))
yml_pfad = (
    sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "workflows", "agent-gate.yml")
)
yml = open(yml_pfad, encoding="utf-8").read()
code = textwrap.dedent(re.search(r"python3 - <<'PY'\n(.*?)\n\s*PY\n", yml, re.S).group(1))
SLUG = re.search(r'AGENT_AUTHORS = \("github-actions\[bot\]", "(.+?)\[bot\]"\)', code).group(1)
if SLUG.startswith("@@"):  # Vorlage mit Platzhalter
    SLUG = "test-app"
    code = code.replace("@@APP_SLUG@@", SLUG)
_tmp = tempfile.mkdtemp()
GATE = os.path.join(_tmp, "gate_extracted.py")
open(GATE, "w", encoding="utf-8").write(code)
SHA = "a" * 40


def datei(name, status="added", patch="@@ -0,0 +1 @@\n+x = 1\n", **kw):
    d = {"filename": name, "status": status, "additions": 1, "deletions": 0, "patch": patch}
    d.update(kw)
    if patch is None:
        d.pop("patch")
    return d


def pr(**kw):
    p = {
        "title": "[agent] Test",
        "additions": 10,
        "deletions": 0,
        "draft": False,
        "auto_merge": None,
        "state": "open",
        "user": {"login": "github-actions[bot]", "type": "Bot"},
        "head": {"sha": SHA, "repo": {"full_name": "o/r"}},
        "base": {"ref": "main", "repo": {"full_name": "o/r"}},
    }
    p.update(kw)
    return p


def run(**kw):
    r = {
        "repository": {"full_name": "o/r"},
        "name": "CI",
        "path": ".github/workflows/ci.yml",
        "event": "pull_request",
        "status": "completed",
        "conclusion": "success",
        "head_sha": SHA,
        "head_repository": {"full_name": "o/r"},
        "pull_requests": [{"number": 5}],
    }
    r.update(kw)
    return r


def checks(sha=SHA, **kw):
    c = {"name": "test", "conclusion": "success", "head_sha": sha, "app": {"id": 15368}}
    c.update(kw)
    return {"total_count": 1, "check_runs": [c]}


def lauf(
    name,
    erwartet,
    dateien=None,
    prd=None,
    rund=None,
    chk=None,
    head=SHA,
    writes=None,
    repo=None,
    check=None,
    prraw=None,
):
    fx = tempfile.mkdtemp()
    for n, v in (
        ("pr", prd or pr()),
        ("run", rund or run()),
        ("checks", chk or checks()),
        ("files", dateien if dateien is not None else [datei("src/p/a.py")]),
        ("repo", repo or {"default_branch": "main", "allow_auto_merge": True}),
    ):
        json.dump(v, open(os.path.join(fx, n + ".json"), "w"))
    if prraw is not None:
        open(os.path.join(fx, "pr.json"), "w").write(prraw)
    env = dict(
        os.environ,
        FIXDIR=fx,
        GH_BIN=f'"{sys.executable}" "{os.path.join(here, "fake_gh.py")}"',
        REPO="o/r",
        RUN_ID="77",
        HEAD_SHA=head,
        PYTHONIOENCODING="utf-8",
    )
    r = subprocess.run(
        [sys.executable, "-I", GATE],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    wl = os.path.join(fx, "writes.log")
    alle = open(wl).read().strip().splitlines() if os.path.exists(wl) else []
    cs = [x for x in alle if x.startswith("check")]
    log = [x for x in alle if not x.startswith("check")]
    ok = (
        (r.returncode == 0) == (erwartet == "pass")
        and (writes is None or log == writes)
        and (check is None or cs == check)
    )
    if check is not None:
        log = log + cs
    print(
        f"{'OK  ' if ok else 'FEHL'} {name:<50} erwartet={erwartet:<4} "
        f"exit={r.returncode} writes={log}"
    )
    if not ok:
        print("     ", r.stdout.strip().replace("\n", " | "), r.stderr.strip()[:300])
    shutil.rmtree(fx)
    return ok


A = ["auto " + SHA]
D = ["disable-auto"]
res = []
R = res.append
# Bisherige Inhalts-Negativtests
R(
    lauf(
        "gueltiger Agenten-PR (src+tests)",
        "pass",
        [datei("src/p/a.py"), datei("tests/test_a.py")],
        writes=A,
    )
)
R(lauf("Draft-PR wird ready + auto", "pass", prd=pr(draft=True), writes=["ready"] + A))
R(lauf("Auto-Merge schon aktiv", "pass", prd=pr(auto_merge={"x": 1}), writes=[]))
R(
    lauf(
        "Mensch als Autor: ignoriert",
        "pass",
        [datei(".github/x.yml")],
        prd=pr(user={"login": "Inzaghi1983b", "type": "User"}),
        writes=[],
    )
)
R(
    lauf(
        "Datei .github/workflows",
        "fail",
        [datei("src/a.py"), datei(".github/workflows/ci.yml")],
        writes=D,
    )
)
R(lauf("AGENTS.md", "fail", [datei("AGENTS.md")], writes=D))
R(lauf("pyproject.toml", "fail", [datei("pyproject.toml")], writes=D))
R(lauf("Wurzel-Datei evil.py", "fail", [datei("evil.py")], writes=D))
R(
    lauf(
        "Rename src -> .github",
        "fail",
        [datei(".github/w.yml", status="renamed", previous_filename="src/a.py")],
        writes=D,
    )
)
R(lauf("Pfad mit /../", "fail", [datei("src/../x.py")], writes=D))
R(
    lauf(
        "Testdatei geloescht",
        "fail",
        [datei("tests/test_a.py", status="removed", patch="@@ -1 +0,0 @@\n-def test_a(): pass\n")],
        writes=D,
    )
)
R(
    lauf(
        "Test mit skip",
        "fail",
        [
            datei(
                "tests/test_a.py",
                patch="@@ -0,0 +1,2 @@\n+@pytest.mark.skip\n+def test_a(): pass\n",
            )
        ],
        writes=D,
    )
)
R(
    lauf(
        "Test mit xfail",
        "fail",
        [datei("tests/test_a.py", patch="@@ -0,0 +1 @@\n+@pytest.mark.xfail\n")],
        writes=D,
    )
)
R(
    lauf(
        "Test mit importorskip",
        "fail",
        [datei("tests/test_a.py", patch="@@ -0,0 +1 @@\n+x = pytest.importorskip('y')\n")],
        writes=D,
    )
)
R(
    lauf(
        "Assertions netto reduziert",
        "fail",
        [
            datei(
                "tests/test_a.py",
                status="modified",
                patch="@@ -1,3 +1,1 @@\n-    assert a == 1\n-    assert b == 2\n"
                "+    assert a == 1\n",
            )
        ],
        writes=D,
    )
)
R(
    lauf(
        "Assertions ersetzt (netto gleich)",
        "pass",
        [
            datei(
                "tests/test_a.py",
                status="modified",
                patch="@@ -1 +1 @@\n-    assert a == 1\n+    assert a == 2\n",
            )
        ],
        writes=A,
    )
)
R(
    lauf(
        "src importiert subprocess",
        "fail",
        [datei("src/p/a.py", patch="@@ -0,0 +1 @@\n+import subprocess\n")],
        writes=D,
    )
)
R(
    lauf(
        "src importiert requests",
        "fail",
        [datei("src/p/a.py", patch="@@ -0,0 +1 @@\n+from requests import get\n")],
        writes=D,
    )
)
R(
    lauf(
        "src os.system",
        "fail",
        [datei("src/p/a.py", patch="@@ -0,0 +1 @@\n+    os.system('x')\n")],
        writes=D,
    )
)
R(
    lauf(
        "src eval",
        "fail",
        [datei("src/p/a.py", patch="@@ -0,0 +1 @@\n+    y = eval(x)\n")],
        writes=D,
    )
)
R(
    lauf(
        "tests duerfen subprocess",
        "pass",
        [datei("tests/test_cli.py", patch="@@ -0,0 +1 @@\n+import subprocess\n")],
        writes=A,
    )
)
R(lauf("Binaerdatei ohne Patch", "fail", [datei("tests/d.bin", patch=None)], writes=D))
R(lauf("zu gross (801 Zeilen)", "fail", prd=pr(additions=801), writes=D))
R(lauf("genau 800 Zeilen ok", "pass", prd=pr(additions=800), writes=A))
R(lauf("Titel ohne Praefix", "fail", prd=pr(title="Sneaky"), writes=D))
R(lauf("51 Dateien", "fail", [datei(f"src/f{i}.py") for i in range(51)], writes=D))
R(lauf("50 Dateien (Paginierung) ok", "pass", [datei(f"src/f{i}.py") for i in range(50)], writes=A))
R(
    lauf(
        "Log-Injection im Patch",
        "fail",
        [datei("src/p/a.py", patch="@@ -0,0 +1 @@\n+import subprocess  ::set-output name=x::y\n")],
        writes=D,
    )
)
# Neue Gegenproben zum workflow_run-Pfad
R(
    lauf(
        "PR-HEAD veraltet (neuer Push nach CI)",
        "fail",
        prd=pr(head={"sha": "b" * 40, "repo": {"full_name": "o/r"}}),
        writes=[],
    )
)
R(lauf("Ereignis-HEAD != Lauf-HEAD", "fail", head="c" * 40, writes=[]))
R(lauf("Lauf ohne PR-Zuordnung", "fail", rund=run(pull_requests=[]), writes=[]))
R(
    lauf(
        "Lauf mit zwei PRs",
        "fail",
        rund=run(pull_requests=[{"number": 5}, {"number": 6}]),
        writes=[],
    )
)
R(lauf("falscher Workflow-Name", "fail", rund=run(name="Evil"), writes=[]))
R(lauf("falscher Workflow-Pfad", "fail", rund=run(path=".github/workflows/evil.yml"), writes=[]))
R(lauf("Lauf aus anderem Repo", "fail", rund=run(repository={"full_name": "x/y"}), writes=[]))
R(lauf("Lauf aus Fork", "fail", rund=run(head_repository={"full_name": "x/y"}), writes=[]))
R(
    lauf(
        "PR-Branch aus Fork",
        "fail",
        prd=pr(head={"sha": SHA, "repo": {"full_name": "x/y"}}),
        writes=[],
    )
)
R(
    lauf(
        "PR nicht gegen Standard-Branch",
        "fail",
        prd=pr(base={"ref": "dev", "repo": {"full_name": "o/r"}}),
        writes=[],
    )
)
R(lauf("PR geschlossen", "fail", prd=pr(state="closed"), writes=[]))
R(lauf("CI-Lauf rot", "fail", rund=run(conclusion="failure"), writes=[]))
R(lauf("CI-Lauf cancelled: nichts tun", "pass", rund=run(conclusion="cancelled"), writes=[]))
R(
    lauf(
        "CI-Lauf action_required: nichts tun",
        "pass",
        rund=run(conclusion="action_required"),
        writes=[],
    )
)
R(
    lauf(
        "CI-Lauf noch nicht fertig",
        "pass",
        rund=run(status="in_progress", conclusion=None),
        writes=[],
    )
)
R(lauf("Lauf nicht pull_request (push)", "pass", rund=run(event="push"), writes=[]))
R(lauf("Pflicht-Check fehlt", "fail", chk={"check_runs": []}, writes=[]))
R(lauf("Pflicht-Check rot", "fail", chk=checks(conclusion="failure"), writes=[]))
R(lauf("Pflicht-Check von falscher App", "fail", chk=checks(app={"id": 1}), writes=[]))
R(lauf("Pflicht-Check fuer anderen Commit", "fail", chk=checks(sha="d" * 40), writes=[]))
R(lauf("Pflicht-Check doppelt", "fail", chk={"check_runs": checks()["check_runs"] * 2}, writes=[]))
APP = {"login": SLUG + "[bot]", "type": "Bot"}
R(lauf("Autor eigene Mini-App: wird geprueft", "pass", prd=pr(user=APP), writes=A))
R(
    lauf(
        "Mini-App mit Verstoss: Auto-Merge aus",
        "fail",
        [datei(".github/x.yml")],
        prd=pr(user=APP),
        writes=D,
    )
)
R(
    lauf(
        "Mini-App mit pyproject.toml", "fail", [datei("pyproject.toml")], prd=pr(user=APP), writes=D
    )
)
R(
    lauf(
        "fremder Bot (dependabot): ignoriert",
        "pass",
        [datei(".github/x.yml")],
        prd=pr(user={"login": "dependabot[bot]", "type": "Bot"}),
        writes=[],
    )
)
R(
    lauf(
        "Mensch mit App-Namen (Typ User): ignoriert",
        "pass",
        [datei(".github/x.yml")],
        prd=pr(user={"login": SLUG + "[bot]", "type": "User"}),
        writes=[],
    )
)
R(
    lauf(
        "aehnlicher Name: ignoriert",
        "pass",
        [datei(".github/x.yml")],
        prd=pr(user={"login": SLUG + "-evil[bot]", "type": "Bot"}),
        writes=[],
    )
)
R(
    lauf(
        "Repo ohne Auto-Merge: keine Integration, kein ready",
        "pass",
        prd=pr(draft=True),
        repo={"default_branch": "main", "allow_auto_merge": False},
        writes=[],
    )
)
R(
    lauf(
        "allow_auto_merge fehlt in API: wie aus", "pass", repo={"default_branch": "main"}, writes=[]
    )
)
R(
    lauf(
        "Repo ohne Auto-Merge, Verstoss: weiter disable-auto",
        "fail",
        [datei("pyproject.toml")],
        repo={"default_branch": "main", "allow_auto_merge": False},
        writes=D,
    )
)

# Check-Run agent-gate (Pflicht-Check im Ruleset)
APPB = {"login": SLUG + "[bot]", "type": "Bot"}
NOAM = {"default_branch": "main", "allow_auto_merge": False}
R(lauf("Check: gueltiger Bot-PR -> success", "pass", check=["check success"], writes=A))
R(
    lauf(
        "Check: gueltiger Bot-PR, Auto-Merge aus -> success, kein Merge",
        "pass",
        repo=NOAM,
        check=["check success"],
        writes=[],
    )
)
R(lauf("Check: App-PR -> success", "pass", prd=pr(user=APPB), check=["check success"], writes=A))
R(
    lauf(
        "Check: Verstoss -> failure",
        "fail",
        [datei("pyproject.toml")],
        check=["check failure"],
        writes=D,
    )
)
R(
    lauf(
        "Check: Mensch -> success (nicht zustaendig)",
        "pass",
        prd=pr(user={"login": "Inzaghi1983b", "type": "User"}),
        check=["check success"],
        writes=[],
    )
)
R(
    lauf(
        "Check: PR-HEAD veraltet -> failure",
        "fail",
        prd=pr(head={"sha": "b" * 40, "repo": {"full_name": "o/r"}}),
        check=["check failure"],
        writes=[],
    )
)
R(
    lauf(
        "Check: CI rot -> failure",
        "fail",
        rund=run(conclusion="failure"),
        check=["check failure"],
        writes=[],
    )
)
R(
    lauf(
        "Check: ohne PR-Zuordnung -> failure",
        "fail",
        rund=run(pull_requests=[]),
        check=["check failure"],
        writes=[],
    )
)
R(
    lauf(
        "Check: Pflicht-Check fehlt -> failure",
        "fail",
        chk={"check_runs": []},
        check=["check failure"],
        writes=[],
    )
)
R(
    lauf(
        "Check: CI cancelled -> kein Check",
        "pass",
        rund=run(conclusion="cancelled"),
        check=[],
        writes=[],
    )
)
R(
    lauf(
        "Check: CI action_required -> kein Check",
        "pass",
        rund=run(conclusion="action_required"),
        check=[],
        writes=[],
    )
)
R(
    lauf(
        "Check: falscher Workflow -> kein Check", "fail", rund=run(name="Evil"), check=[], writes=[]
    )
)
R(
    lauf(
        "Check: Fork-Lauf -> kein Check",
        "fail",
        rund=run(head_repository={"full_name": "x/y"}),
        check=[],
        writes=[],
    )
)
R(
    lauf(
        "Check: kaputte API-Antwort -> kein Check (fail closed)",
        "fail",
        prraw="{kaputt",
        check=[],
        writes=[],
    )
)
CHK = checks()
CHK["check_runs"].append(
    {"name": "agent-gate", "conclusion": "failure", "head_sha": SHA, "app": {"id": 15368}, "id": 99}
)
R(
    lauf(
        "Check: vorhandener agent-gate wird aktualisiert statt doppelt",
        "pass",
        chk=CHK,
        check=["check-patch success"],
        writes=A,
    )
)

# --- A1: geschuetzte Akzeptanztests und deklarierte Abweichungen ---
AKZ = "tests/akzeptanz/test_x.py"
R(lauf("A1: Bot legt Akzeptanztest an", "fail", [datei(AKZ)], check=["check failure"], writes=D))
R(
    lauf(
        "A1: Bot aendert Akzeptanztest",
        "fail",
        [datei(AKZ, status="modified")],
        check=["check failure"],
        writes=D,
    )
)
R(
    lauf(
        "A1: Bot loescht Akzeptanztest",
        "fail",
        [datei(AKZ, status="removed", patch="@@ -1 +0,0 @@\n-def test_a(): pass\n")],
        writes=D,
    )
)
R(
    lauf(
        "A1: Rename aus akzeptanz heraus",
        "fail",
        [datei("tests/test_x.py", status="renamed", previous_filename=AKZ)],
        writes=D,
    )
)
R(
    lauf(
        "A1: Rename nach akzeptanz hinein",
        "fail",
        [datei(AKZ, status="renamed", previous_filename="tests/test_x.py")],
        writes=D,
    )
)
R(
    lauf(
        "A1: Gross-/Kleinschreibung Tests/Akzeptanz",
        "fail",
        [datei("tests/Akzeptanz/test_x.py")],
        writes=D,
    )
)
R(
    lauf(
        "A1: App-PR mit Akzeptanztest",
        "fail",
        [datei(AKZ)],
        prd=pr(user=APP),
        check=["check failure"],
        writes=D,
    )
)
R(
    lauf(
        "A1: aehnlicher Ordner tests/akzeptanz_alt ok",
        "pass",
        [datei("tests/akzeptanz_alt/test_x.py")],
        writes=A,
    )
)
R(lauf("A1: src/akzeptanz ok", "pass", [datei("src/akzeptanz/x.py")], writes=A))
for n, body in (
    ("Zeile ABWEICHUNG:", "## Aenderung\nABWEICHUNG: AC 3 anders umgesetzt\n"),
    ("kleingeschrieben", "abweichung: AC 3 anders"),
    ("Markdown fett", "- **ABWEICHUNG:** AC 3 anders"),
    ("Zitat", "> ABWEICHUNG: AC 3 anders"),
    ("eingerueckt", "   ABWEICHUNG: AC 3 anders"),
    ("leer (unfertig)", "ABWEICHUNG:"),
    ("Log-Injection", "ABWEICHUNG: ::set-output name=x::y"),
):
    R(
        lauf(
            f"A1: {n} -> failure, kein Merge",
            "fail",
            prd=pr(body=body),
            check=["check failure"],
            writes=D,
        )
    )
for n, body in (
    ("ABWEICHUNG: keine", "ABWEICHUNG: keine"),
    ("ABWEICHUNG: -", "ABWEICHUNG: -"),
    ("ABWEICHUNG: nein.", "**ABWEICHUNG:** nein."),
    ("Abweichungen: keine (anderes Wort)", "Abweichungen: keine"),
    ("Prosa keine Abweichung", "Es gibt keine Abweichung vom Auftrag."),
    ("Prosa mit Doppelpunkt davor", "Hinweis: Abweichung wurde nicht noetig"),
    ("kein Body", None),
):
    R(lauf(f"A1: {n} -> ok", "pass", prd=pr(body=body), check=["check success"], writes=A))
R(
    lauf(
        "A1: ABWEICHUNG bei App-PR",
        "fail",
        prd=pr(user=APP, body="ABWEICHUNG: x"),
        check=["check failure"],
        writes=D,
    )
)
R(
    lauf(
        "A1: Mensch-PR mit ABWEICHUNG: ignoriert",
        "pass",
        prd=pr(user={"login": "Inzaghi1983b", "type": "User"}, body="ABWEICHUNG: x"),
        check=["check success"],
        writes=[],
    )
)
R(
    lauf(
        "A1: ABWEICHUNG bei Auto-Merge aus: failure",
        "fail",
        prd=pr(body="ABWEICHUNG: x"),
        repo={"default_branch": "main", "allow_auto_merge": False},
        check=["check failure"],
        writes=D,
    )
)

# Replay mit den echten PR-Texten aus ch-import (Stand 2026-10-18). Die Texte enthalten noch keine
# ABWEICHUNG-Zeile (Regel neu): erwartet keine Falsch-Positive. Mit Zeile muss es rot werden.
fx_dir = os.path.join(here, "fixtures")
for nr in (24, 25, 30, 37):
    body = open(os.path.join(fx_dir, f"pr-{nr}-body.md"), encoding="utf-8").read()
    R(
        lauf(
            f"A1 Replay PR #{nr}: unveraendert ok",
            "pass",
            prd=pr(user=APP, body=body),
            check=["check success"],
            writes=A,
        )
    )
    R(
        lauf(
            f"A1 Replay PR #{nr}: mit ABWEICHUNG-Zeile rot",
            "fail",
            prd=pr(user=APP, body=body + "\nABWEICHUNG: Acceptance Criterion anders umgesetzt\n"),
            check=["check failure"],
            writes=D,
        )
    )
print("ALLE OK" if all(res) else f"{res.count(False)} FEHLER", f"({len(res)} Faelle)")
sys.exit(0 if all(res) else 1)

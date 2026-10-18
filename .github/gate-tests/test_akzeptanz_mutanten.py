"""Beweis, dass die Akzeptanztests eine fachlich falsche Umsetzung erkennen.

Aufruf (vom Repo-Wurzelverzeichnis): python .github/gate-tests/test_akzeptanz_mutanten.py
Die echte Umsetzung (src/chimport/jahr.py) muss gegen tests/akzeptanz/test_jahr.py bestehen; jede
absichtlich falsche Variante muss daran scheitern. Ausserdem: Modul fehlt -> Spec wartet (skip),
Modul defekt -> Spec rot. Exit-Code 0 nur, wenn alles wie erwartet ausfaellt.
"""

import os
import shutil
import subprocess
import sys
import tempfile

WURZEL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC = os.path.join(WURZEL, "tests", "akzeptanz", "test_jahr.py")
ECHT = os.path.join(WURZEL, "src", "chimport", "jahr.py")

KOPF = '''"""Mutant."""
ZIFFERN = frozenset("0123456789")


def ist_jahr(wert: str) -> bool:
'''

BASIS = "len(t) == 4 and t.isascii() and t.isdigit()"


def mutant(*zeilen):
    return KOPF + "".join("    " + z + "\n" for z in zeilen)


MUTANTEN = {
    "Untergrenze 1800 statt 1900": mutant(
        "t = wert.strip()", f"return {BASIS} and 1800 <= int(t) <= 2100"
    ),
    "Obergrenze exklusiv (2100 abgelehnt)": mutant(
        "t = wert.strip()", f"return {BASIS} and 1900 <= int(t) < 2100"
    ),
    "str.isdigit ohne ASCII-Pruefung (arabische Ziffern)": mutant(
        "t = wert.strip()", "return len(t) == 4 and t.isdigit() and 1900 <= int(t) <= 2100"
    ),
    "kein strip (Leerraum ungueltig)": mutant(
        "t = wert", f"return {BASIS} and 1900 <= int(t) <= 2100"
    ),
    "Rueckgabe nicht bool": mutant(
        "t = wert.strip()",
        f"if {BASIS} and 1900 <= int(t) <= 2100:",
        "    return 1",
        "return 0",
    ),
    "wirft bei Muell statt False": mutant("t = wert.strip()", "return 1900 <= int(t) <= 2100"),
    "zweistellige Jahre erlaubt": mutant(
        "t = wert.strip()",
        "zusatz = 1900 if len(t) == 2 else 0",
        "return t.isascii() and t.isdigit() and 1900 <= int(t) + zusatz <= 2100",
    ),
}


def pytest_lauf(src_wurzel, spec_pfad, cwd):
    env = dict(os.environ, PYTHONPATH=src_wurzel, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", spec_pfad],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
        env=env,
    )


def baue(inhalt):
    """Temp-Projekt mit Paket chimport; inhalt=None -> Modul fehlt."""
    d = tempfile.mkdtemp()
    pkg = os.path.join(d, "src", "chimport")
    os.makedirs(pkg)
    open(os.path.join(pkg, "__init__.py"), "w").close()
    if inhalt is not None:
        open(os.path.join(pkg, "jahr.py"), "w", encoding="utf-8").write(inhalt)
    spec = os.path.join(d, "test_spec.py")
    shutil.copy(SPEC, spec)
    return d, spec


ergebnisse = []


def pruefe(name, ok, detail=""):
    ergebnisse.append(ok)
    print(f"{'OK  ' if ok else 'FEHL'} {name} {detail}", flush=True)


# 1) korrekte Umsetzung besteht
d, spec = baue(open(ECHT, encoding="utf-8").read())
r = pytest_lauf(os.path.join(d, "src"), spec, d)
pruefe("korrekte Umsetzung besteht", r.returncode == 0, r.stdout.strip().splitlines()[-1])
shutil.rmtree(d)

# 2) jede fachlich falsche Umsetzung scheitert
for name, code in MUTANTEN.items():
    d, spec = baue(code)
    r = pytest_lauf(os.path.join(d, "src"), spec, d)
    pruefe(f"Mutant scheitert: {name}", r.returncode != 0, r.stdout.strip().splitlines()[-1])
    shutil.rmtree(d)

# 3) Waechter fuer neue Module: Datei fehlt -> Spec wartet (skip), Datei defekt -> rot
GUARD_SPEC = """
import importlib.util

import pytest

if importlib.util.find_spec("chimport.jahr") is None:
    pytest.skip("Modul noch nicht umgesetzt", allow_module_level=True)

from chimport.jahr import ist_jahr  # noqa: E402


def test_x():
    assert ist_jahr("1999") is True
"""
for name, inhalt, erwartet_ok in (
    ("Waechter: Modul fehlt -> Spec wartet", None, True),
    ("Waechter: Modul defekt (Syntaxfehler) -> rot", "def ist_jahr(:\n", False),
    ("Waechter: Modul falsch -> rot", KOPF + "    return False\n", False),
    ("Waechter: Modul richtig -> gruen", open(ECHT, encoding="utf-8").read(), True),
):
    d, spec = baue(inhalt)
    open(spec, "w", encoding="utf-8").write(GUARD_SPEC)
    r = pytest_lauf(os.path.join(d, "src"), spec, d)
    ok = (r.returncode == 0) == erwartet_ok
    if name.endswith("wartet"):
        # Reiner Modul-Skip gibt pytest-Exit-Code 5 (nichts gesammelt); im Gesamtlauf bleibt es 0.
        ok = r.returncode in (0, 5) and "skipped" in r.stdout
    pruefe(name, ok, r.stdout.strip().splitlines()[-1])
    shutil.rmtree(d)

print(
    "ALLE OK" if all(ergebnisse) else f"{ergebnisse.count(False)} FEHLER",
    f"({len(ergebnisse)} Faelle)",
)
sys.exit(0 if all(ergebnisse) else 1)

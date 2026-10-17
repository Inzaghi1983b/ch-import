import os
import subprocess
import sys
from pathlib import Path

from chimport.cli import main

# Alle Testwerte sind erfunden bzw. selbst berechnet und keine echten Personendaten.

REPO = Path(__file__).resolve().parents[1]


def _schreibe(tmp_path: Path, inhalt: str) -> Path:
    pfad = tmp_path / "daten.csv"
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad


def test_pruefe_ohne_fehler_exit_0(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz;geburt\n8001;29.02.2024\n")

    code = main(["pruefe", str(pfad), "--schema", "plz=plz,geburt=datum"])

    ausgabe = capsys.readouterr()
    assert code == 0
    assert ausgabe.out == ""
    assert ausgabe.err == ""


def test_pruefe_mit_fehlern_exit_1(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz;geburt\n99999;31.04.2024\n")

    code = main(["pruefe", str(pfad), "--schema", "plz=plz,geburt=datum"])

    ausgabe = capsys.readouterr()
    assert code == 1
    assert ausgabe.out == (
        'Zeile 2, Spalte plz: "99999" ist keine gueltige plz\n'
        'Zeile 2, Spalte geburt: "31.04.2024" ist keine gueltige datum\n'
    )
    assert ausgabe.err == ""


def test_pruefe_fehlende_datei_exit_2(tmp_path, capsys):
    pfad = tmp_path / "fehlt.csv"

    code = main(["pruefe", str(pfad), "--schema", "plz=plz"])

    ausgabe = capsys.readouterr()
    assert code == 2
    assert ausgabe.out == ""
    assert "fehlt.csv" in ausgabe.err
    assert "Traceback" not in ausgabe.err


def test_pruefe_unbekannter_typ_exit_2(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz\n8001\n")

    code = main(["pruefe", str(pfad), "--schema", "plz=zahl"])

    ausgabe = capsys.readouterr()
    assert code == 2
    assert ausgabe.out == ""
    assert "zahl" in ausgabe.err


def test_pruefe_aufruffehler_exit_2(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz\n8001\n")

    code = main(["pruefe", str(pfad)])

    ausgabe = capsys.readouterr()
    assert code == 2
    assert ausgabe.out == ""
    assert "usage:" in ausgabe.err


def test_normalisiere_auf_stdout_exit_0(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz;name\nCH-8001;Beispiel\n")

    code = main(["normalisiere", str(pfad), "--schema", "plz=plz"])

    ausgabe = capsys.readouterr()
    assert code == 0
    assert ausgabe.out == "plz;name\n8001;Beispiel\n"
    assert ausgabe.err == ""


def test_normalisiere_in_datei_exit_0(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "PLZ;Ort\nCH-8001;Zürich\n")
    ausgabe_pfad = tmp_path / "aus.csv"

    code = main(
        [
            "normalisiere",
            str(pfad),
            "--schema",
            "PLZ=plz",
            "--ausgabe",
            str(ausgabe_pfad),
        ]
    )

    ausgabe = capsys.readouterr()
    assert code == 0
    assert ausgabe.out == ""
    assert ausgabe.err == ""
    assert ausgabe_pfad.read_text(encoding="utf-8") == "PLZ;Ort\n8001;Zürich\n"


def test_normalisiere_mit_fehlern_exit_1_und_keine_ausgabe(tmp_path, capsys):
    pfad = _schreibe(tmp_path, "plz;name\n99999;Beispiel\n")
    ausgabe_pfad = tmp_path / "aus.csv"
    ausgabe_pfad.write_text("unveraendert", encoding="utf-8")

    code = main(
        [
            "normalisiere",
            str(pfad),
            "--schema",
            "plz=plz",
            "--ausgabe",
            str(ausgabe_pfad),
        ]
    )

    ausgabe = capsys.readouterr()
    assert code == 1
    assert ausgabe.out == 'Zeile 2, Spalte plz: "99999" ist keine gueltige plz\n'
    assert ausgabe.err == ""
    assert ausgabe_pfad.read_text(encoding="utf-8") == "unveraendert"


def test_normalisiere_fehlende_datei_exit_2(tmp_path, capsys):
    pfad = tmp_path / "fehlt.csv"

    code = main(["normalisiere", str(pfad), "--schema", "plz=plz"])

    ausgabe = capsys.readouterr()
    assert code == 2
    assert ausgabe.out == ""
    assert "fehlt.csv" in ausgabe.err
    assert "Traceback" not in ausgabe.err


def test_python_m_chimport(tmp_path):
    pfad = _schreibe(tmp_path, "plz\n99999\n")
    umgebung = os.environ.copy()
    umgebung["PYTHONPATH"] = str(REPO / "src")

    ergebnis = subprocess.run(
        [sys.executable, "-m", "chimport", "pruefe", str(pfad), "--schema", "plz=plz"],
        cwd=REPO,
        env=umgebung,
        capture_output=True,
        text=True,
        check=False,
    )

    assert ergebnis.returncode == 1
    assert ergebnis.stdout == 'Zeile 2, Spalte plz: "99999" ist keine gueltige plz\n'
    assert ergebnis.stderr == ""

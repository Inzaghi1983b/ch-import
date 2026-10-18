"""Akzeptanztest (spec-first) fuer chimport.laendercode.

Von Menschen vorab festgelegt und per Pull Request gemergt, bevor das Issue das Label `agent` bekam.
Coding-Agenten duerfen diese Datei nicht anlegen, aendern, loeschen oder umbenennen (Agent-Gate,
AGENTS.md). Stufe-D-Test: Leerraum am Rand gehoert NICHT zum Code und macht ihn ungueltig; das
widerspricht absichtlich der allgemeinen Regel in AGENTS.md (Leerraum ignorieren).

Der Waechter ueberspringt die Datei nur, solange die Quelldatei fehlt (siehe README.md).
"""

import importlib.util

import pytest

if importlib.util.find_spec("chimport.laendercode") is None:
    pytest.skip("Modul noch nicht umgesetzt", allow_module_level=True)

from chimport.laendercode import ist_laendercode  # noqa: E402

GUELTIG = ["CH", "DE", "FR", "IT", "AT", "LI"]
UNGUELTIG = ["", "ch", "Ch", " CH", "CH ", "C H", "CHE", "C", "XX", "ÄT", "DÉ"]


@pytest.mark.parametrize("wert", GUELTIG)
def test_gueltige_laendercodes(wert):
    assert ist_laendercode(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIG)
def test_ungueltige_laendercodes(wert):
    assert ist_laendercode(wert) is False


def test_leerraum_am_rand_ist_ungueltig():
    assert ist_laendercode(" CH") is False
    assert ist_laendercode("CH ") is False
    assert ist_laendercode("\tCH") is False

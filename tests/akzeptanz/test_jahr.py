"""Akzeptanztest (spec-first) fuer chimport.jahr.

Von Menschen vorab festgelegt und per Pull Request gemergt, bevor das Issue das Label `agent` bekam.
Coding-Agenten duerfen diese Datei nicht anlegen, aendern, loeschen oder umbenennen (Agent-Gate,
AGENTS.md). Quelle der Beispiele: Acceptance Criteria von Issue #36.
"""

import pytest

from chimport.jahr import ist_jahr

GUELTIG = ["1900", "1999", " 2024 ", "2100"]
UNGUELTIG = ["", "1899", "2101", "99", "20245", "20a4", "٢٠٢٤"]


@pytest.mark.parametrize("wert", GUELTIG)
def test_gueltige_jahre(wert):
    assert ist_jahr(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIG)
def test_ungueltige_jahre(wert):
    assert ist_jahr(wert) is False


def test_grenzen_sind_inklusive():
    assert ist_jahr("1900") is True
    assert ist_jahr("2100") is True
    assert ist_jahr("1899") is False
    assert ist_jahr("2101") is False

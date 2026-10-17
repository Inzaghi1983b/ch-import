import re

import pytest

from chimport.telefon import ist_gueltige_telefonnummer, normalisiere_telefonnummer

GUELTIGE_FAELLE = [
    ("+41791234567", "+41 79 123 45 67"),
    ("0041 79 123 45 67", "+41 79 123 45 67"),
    ("+41 (0)79 123 45 67", "+41 79 123 45 67"),
    ("031 123 45 67", "+41 31 123 45 67"),
    ("044/123.45.67", "+41 44 123 45 67"),
    ("079 123 45 67", "+41 79 123 45 67"),
    ("0791234567", "+41 79 123 45 67"),
    ("+41-79-123-45-67", "+41 79 123 45 67"),
    (" 079 123 45 67 ", "+41 79 123 45 67"),
    ("(044) 123 45 67", "+41 44 123 45 67"),
    ("021 123 45 67", "+41 21 123 45 67"),
    ("091 123 45 67", "+41 91 123 45 67"),
]

UNGUELTIGE_FAELLE = [
    "+49 30 123456",
    "079 123 45 6",
    "079 123 45 678",
    "011 123 45 67",
    "+41 79 123 45 6a",
    "",
    "   ",
    "٠٧٩ ١٢٣ ٤٥ ٦٧",
    "079 123 45 6٣",
    "179 123 45 67",
    "41 79 123 45 67",
    "079) 123 45 67",
    "079 (123 45 67",
    "079 () 123 45 67",
    "+41 (0)079 123 45 67",
]


@pytest.mark.parametrize(("eingabe", "erwartet"), GUELTIGE_FAELLE)
def test_normalisiere_gueltiger_nummern(eingabe, erwartet):
    assert normalisiere_telefonnummer(eingabe) == erwartet


@pytest.mark.parametrize(("eingabe", "erwartet"), GUELTIGE_FAELLE)
def test_ist_gueltige_bei_gueltigen_nummern(eingabe, erwartet):
    assert ist_gueltige_telefonnummer(eingabe) is True


@pytest.mark.parametrize("eingabe", UNGUELTIGE_FAELLE)
def test_ist_ungueltig_bei_ungueltigen_nummern(eingabe):
    assert ist_gueltige_telefonnummer(eingabe) is False


@pytest.mark.parametrize("eingabe", UNGUELTIGE_FAELLE)
def test_normalisiere_wirft_valueerror(eingabe):
    with pytest.raises(ValueError):
        normalisiere_telefonnummer(eingabe)


@pytest.mark.parametrize(("eingabe", "erwartet"), GUELTIGE_FAELLE)
def test_normalisierung_ist_idempotent(eingabe, erwartet):
    assert normalisiere_telefonnummer(erwartet) == erwartet


@pytest.mark.parametrize(("eingabe", "erwartet"), GUELTIGE_FAELLE)
def test_ausgabe_folgt_standardschreibweise(eingabe, erwartet):
    assert re.fullmatch(r"\+41 [2-9][0-9] [0-9]{3} [0-9]{2} [0-9]{2}", erwartet)


def test_ist_gueltige_wirft_bei_keiner_eingabe():
    for eingabe in [*UNGUELTIGE_FAELLE, "a", "+", "0", "(0)", "+41 (0)"]:
        assert ist_gueltige_telefonnummer(eingabe) is False

from decimal import Decimal

import pytest

from chimport.betrag import (
    ist_gueltiger_betrag,
    normalisiere_betrag,
    runde_auf_5_rappen,
)

GUELTIGE_BETRAEGE = [
    ("CHF 1'234.5", "1234.50"),
    ("1'234.5", "1234.50"),
    ("chf 1234.5", "1234.50"),
    ("1234.5 CHF", "1234.50"),
    ("1234.50", "1234.50"),
    ("0.05", "0.05"),
    ("-0.05", "-0.05"),
    ("-0", "0.00"),
    ("0", "0.00"),
    ("CHF -12.00", "-12.00"),
    ("-12.00 CHF", "-12.00"),
    ("1'000'000.00", "1000000.00"),
    ("1’234.5", "1234.50"),
    ("  CHF 99.99  ", "99.99"),
    ("0.00", "0.00"),
]

UNGUELTIGE_BETRAEGE = [
    "",
    "   ",
    "1,50",
    "1.234",
    "1''234.00",
    "12'34.00",
    "1.5.0",
    "abc",
    "CHF",
    "1e3",
    "٣.٠٠",
    "1.234'567.00",
    "'1234.00",
    "1234.00'",
    "1.2345",
    "CHF CHF 10.00",
    "10.00 EUR",
    "--10.00",
    "10-",
    "+10.00",
]


@pytest.mark.parametrize(("eingabe", "erwartet"), GUELTIGE_BETRAEGE)
def test_normalisiere_betrag_gibt_standardschreibweise_zurueck(eingabe, erwartet):
    assert normalisiere_betrag(eingabe) == erwartet


@pytest.mark.parametrize("eingabe", UNGUELTIGE_BETRAEGE)
def test_normalisiere_betrag_wirft_valueerror(eingabe):
    with pytest.raises(ValueError):
        normalisiere_betrag(eingabe)


@pytest.mark.parametrize("eingabe", [wert for wert, _ in GUELTIGE_BETRAEGE])
def test_ist_gueltiger_betrag_akzeptiert_gueltige_eingaben(eingabe):
    assert ist_gueltiger_betrag(eingabe) is True


@pytest.mark.parametrize("eingabe", UNGUELTIGE_BETRAEGE)
def test_ist_gueltiger_betrag_lehnt_ungueltige_eingaben_ab(eingabe):
    assert ist_gueltiger_betrag(eingabe) is False


def test_ist_gueltiger_betrag_wirft_nie():
    assert ist_gueltiger_betrag(None) is False
    assert ist_gueltiger_betrag(12) is False
    assert ist_gueltiger_betrag(12.5) is False


@pytest.mark.parametrize("eingabe", [wert for wert, _ in GUELTIGE_BETRAEGE])
def test_pruefen_und_normalisieren_stimmen_ueberein(eingabe):
    assert ist_gueltiger_betrag(eingabe) is True
    assert normalisiere_betrag(eingabe) != ""


@pytest.mark.parametrize(
    ("betrag", "erwartet"),
    [
        ("1.025", "1.05"),
        ("1.02", "1.00"),
        ("-1.025", "-1.05"),
        ("1.00", "1.00"),
        ("1.05", "1.05"),
        ("1.074", "1.05"),
        ("1.076", "1.10"),
        ("0.00", "0.00"),
        ("-0.02", "0.00"),
        ("0.03", "0.05"),
        ("9999999999.99", "10000000000.00"),
    ],
)
def test_runde_auf_5_rappen(betrag, erwartet):
    ergebnis = runde_auf_5_rappen(Decimal(betrag))
    assert ergebnis == Decimal(erwartet)
    assert isinstance(ergebnis, Decimal)
    assert ergebnis.as_tuple().exponent == -2

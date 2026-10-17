import pytest

from chimport.waehrung import ist_waehrung

GUELTIGE_WAEHRUNGEN = [
    "CHF",
    "EUR",
    "USD",
    "GBP",
    " CHF ",
    "EUR\n",
]

UNGUELTIGE_WAEHRUNGEN = [
    "",
    "chf",
    "JPY",
    "CH",
    "CHFF",
    "ЕUR",  # kyrillisches E
    "EURO",
    "CH F",
    "CHF EUR",
]


@pytest.mark.parametrize("wert", GUELTIGE_WAEHRUNGEN)
def test_ist_waehrung_gueltig(wert: str) -> None:
    assert ist_waehrung(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIGE_WAEHRUNGEN)
def test_ist_waehrung_ungueltig(wert: str) -> None:
    assert ist_waehrung(wert) is False


def test_ist_waehrung_wirft_nie() -> None:
    for wert in ["", "abc", "٣", None]:
        assert ist_waehrung(wert) is False

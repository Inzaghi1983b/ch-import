import pytest

from chimport.jahr import ist_jahr

GUELTIGE_JAHRE = [
    "1900",
    "1999",
    "2024",
    "2100",
    " 2024 ",
    "1900\n",
]

UNGUELTIGE_JAHRE = [
    "",
    "1899",
    "2101",
    "99",
    "20245",
    "20a4",
    "٢٠٢٤",
    "  ",
    "2024-",
    "+2024",
    "1 900",
]


@pytest.mark.parametrize("wert", GUELTIGE_JAHRE)
def test_ist_jahr_gueltig(wert: str) -> None:
    assert ist_jahr(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIGE_JAHRE)
def test_ist_jahr_ungueltig(wert: str) -> None:
    assert ist_jahr(wert) is False


def test_grenzen_des_jahres() -> None:
    assert ist_jahr("1900") is True
    assert ist_jahr("1899") is False
    assert ist_jahr("2100") is True
    assert ist_jahr("2101") is False


def test_ist_jahr_wirft_nie() -> None:
    for wert in ["", "abc", "٣", "  ", "٢٠٢٤", None, 2024]:
        assert ist_jahr(wert) is False

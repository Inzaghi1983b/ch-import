import pytest

from chimport.laendercode import ist_laendercode

GUELTIGE_LAENDERCODES = ["CH", "DE", "FR", "IT", "AT", "LI"]

UNGUELTIGE_LAENDERCODES = [
    "",
    "ch",
    "Ch",
    " CH",
    "CH ",
    "\tCH",
    "C H",
    "CHE",
    "C",
    "XX",
    "ÄT",
    "DÉ",
]


@pytest.mark.parametrize("wert", GUELTIGE_LAENDERCODES)
def test_ist_laendercode_gueltig(wert: str) -> None:
    assert ist_laendercode(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIGE_LAENDERCODES)
def test_ist_laendercode_ungueltig(wert: str) -> None:
    assert ist_laendercode(wert) is False


def test_leerraum_am_rand_ist_ungueltig() -> None:
    assert ist_laendercode(" CH") is False
    assert ist_laendercode("CH ") is False
    assert ist_laendercode("\tCH") is False


def test_ist_laendercode_wirft_nie() -> None:
    for wert in ["", "abc", "ÄT", None, 123]:
        assert ist_laendercode(wert) is False

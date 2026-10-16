import pytest

from chimport.plz import ist_gueltige_plz, normalisiere_plz

GUELTIGE_PLZ = [
    "8001",
    " 1000 ",
    "9658",
    "ch-3011",
    "FL-9490",
    "CH-8001",
    "Fl-1000",
    "CH-8001 ",
    "8001\n",
]

UNGUELTIGE_PLZ = [
    "",
    "999",
    "0999",
    "9659",
    "80010",
    "80a1",
    "D-8001",
    "٨٠٠١",
    "8 001",
    "CH-",
    " CH - 8001 ",
    "800-1",
]


@pytest.mark.parametrize("wert", GUELTIGE_PLZ)
def test_ist_gueltige_plz(wert: str) -> None:
    assert ist_gueltige_plz(wert) is True


@pytest.mark.parametrize("wert", GUELTIGE_PLZ)
def test_normalisiere_plz_gibt_vier_ziffern(wert: str) -> None:
    ergebnis = normalisiere_plz(wert)
    assert len(ergebnis) == 4
    assert ergebnis.isascii()


@pytest.mark.parametrize("wert", UNGUELTIGE_PLZ)
def test_ist_gueltige_plz_ungueltig(wert: str) -> None:
    assert ist_gueltige_plz(wert) is False


@pytest.mark.parametrize("wert", UNGUELTIGE_PLZ)
def test_normalisiere_plz_ungueltig(wert: str) -> None:
    with pytest.raises(ValueError):
        normalisiere_plz(wert)


@pytest.mark.parametrize(
    ("wert", "erwartet"),
    [
        ("8001", "8001"),
        (" 1000 ", "1000"),
        ("ch-3011", "3011"),
        ("FL-9490", "9490"),
        ("CH-9658", "9658"),
    ],
)
def test_normalisiere_plz_wert(wert: str, erwartet: str) -> None:
    assert normalisiere_plz(wert) == erwartet


def test_grenzen_der_plz() -> None:
    assert ist_gueltige_plz("1000") is True
    assert ist_gueltige_plz("999") is False
    assert ist_gueltige_plz("9658") is True
    assert ist_gueltige_plz("9659") is False


def test_ist_gueltige_plz_wirft_nie() -> None:
    for wert in ["", "abc", "٣", "  ", "CH-", "٨٠٠١"]:
        assert ist_gueltige_plz(wert) is False


def test_konsistenz_von_pruefung_und_normalisierung() -> None:
    for wert in GUELTIGE_PLZ + UNGUELTIGE_PLZ:
        try:
            normalisiere_plz(wert)
        except ValueError:
            assert ist_gueltige_plz(wert) is False
        else:
            assert ist_gueltige_plz(wert) is True

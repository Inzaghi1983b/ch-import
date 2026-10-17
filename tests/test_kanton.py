import pytest

from chimport.kanton import ist_kanton, normalisiere_kanton

KANTONE = [
    "AG",
    "AI",
    "AR",
    "BE",
    "BL",
    "BS",
    "FR",
    "GE",
    "GL",
    "GR",
    "JU",
    "LU",
    "NE",
    "NW",
    "OW",
    "SG",
    "SH",
    "SO",
    "SZ",
    "TG",
    "TI",
    "UR",
    "VD",
    "VS",
    "ZG",
    "ZH",
]

GUELTIGE_KANTONE = [
    "ZH",
    "be",
    " Ge ",
    "zh ",
    " ZH\n",
    "ag",
    *KANTONE,
]

UNGUELTIGE_KANTONE = [
    "",
    " ",
    "XX",
    "Z",
    "ZHH",
    "Z H",
    "ÄG",
    "Zürich",
    "ZZ",
    "ZH ZH",
    "1H",
]


@pytest.mark.parametrize("wert", GUELTIGE_KANTONE)
def test_ist_kanton(wert: str) -> None:
    assert ist_kanton(wert) is True


@pytest.mark.parametrize("wert", UNGUELTIGE_KANTONE)
def test_ist_kanton_ungueltig(wert: str) -> None:
    assert ist_kanton(wert) is False


@pytest.mark.parametrize("wert", UNGUELTIGE_KANTONE)
def test_normalisiere_kanton_ungueltig(wert: str) -> None:
    with pytest.raises(ValueError):
        normalisiere_kanton(wert)


@pytest.mark.parametrize(
    ("wert", "erwartet"),
    [
        ("ZH", "ZH"),
        ("be", "BE"),
        (" Ge ", "GE"),
        ("zh ", "ZH"),
        (" ZH\n", "ZH"),
        ("vs", "VS"),
    ],
)
def test_normalisiere_kanton_wert(wert: str, erwartet: str) -> None:
    assert normalisiere_kanton(wert) == erwartet


def test_alle_26_kantone() -> None:
    assert len(KANTONE) == 26
    for kuerzel in KANTONE:
        assert ist_kanton(kuerzel) is True
        assert normalisiere_kanton(kuerzel.lower()) == kuerzel


def test_konsistenz_von_pruefung_und_normalisierung() -> None:
    for wert in GUELTIGE_KANTONE + UNGUELTIGE_KANTONE:
        try:
            normalisiere_kanton(wert)
        except ValueError:
            assert ist_kanton(wert) is False
        else:
            assert ist_kanton(wert) is True

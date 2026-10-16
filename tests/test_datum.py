import pytest

from chimport.datum import ist_gueltiges_datum, normalisiere_datum


@pytest.mark.parametrize(
    ("wert", "erwartet"),
    [
        ("29.02.2024", "2024-02-29"),
        ("1.3.2023", "2023-03-01"),
        ("01.03.2023", "2023-03-01"),
        ("2023-03-01", "2023-03-01"),
        ("  1.3.2023  ", "2023-03-01"),
        ("1.1.1900", "1900-01-01"),
        ("31.12.2100", "2100-12-31"),
        ("29.02.2000", "2000-02-29"),
    ],
)
def test_normalisiere_datum_gibt_iso(wert, erwartet):
    assert normalisiere_datum(wert) == erwartet


@pytest.mark.parametrize(
    "wert",
    [
        "29.02.2023",
        "31.04.2024",
        "32.01.2024",
        "01.01.24",
        "01.01.1899",
        "2024/01/01",
        "01.13.2024",
        "",
        "٠١.٠١.٢٠٢٤",
        "2024-1-1",
        "1.1.24",
        "29.02.2100",
        "00.01.2024",
        "01.00.2024",
        "1.1.20240",
        "abc",
        "01.01.2024 extra",
    ],
)
def test_normalisiere_datum_wirft_bei_ungueltig(wert):
    with pytest.raises(ValueError):
        normalisiere_datum(wert)


@pytest.mark.parametrize(
    "wert",
    [
        "29.02.2024",
        "1.3.2023",
        "2023-03-01",
        "  01.01.1900  ",
        "31.12.2100",
    ],
)
def test_ist_gueltiges_datum_wahr(wert):
    assert ist_gueltiges_datum(wert) is True


@pytest.mark.parametrize(
    "wert",
    [
        "29.02.2023",
        "31.04.2024",
        "32.01.2024",
        "01.01.24",
        "01.01.1899",
        "2024/01/01",
        "01.13.2024",
        "",
        "٠١.٠١.٢٠٢٤",
        "31.12.2101",
        "29.02.2100",
        "2024-1-1",
        None,
        20240101,
    ],
)
def test_ist_gueltiges_datum_falsch_ohne_ausnahme(wert):
    assert ist_gueltiges_datum(wert) is False


def test_ist_gueltiges_datum_wirft_nie():
    for wert in ("", "x", "٣٢.٠١.٢٠٢٤", "9999-99-99", ".."):
        assert ist_gueltiges_datum(wert) is False


@pytest.mark.parametrize("wert", ["29.02.2024", "1.3.2023", "2023-03-01"])
def test_gueltig_genau_dann_wenn_normalisierung_klappt(wert):
    assert ist_gueltiges_datum(wert) is True
    assert normalisiere_datum(wert) != ""

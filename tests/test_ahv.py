import pytest

from chimport.ahv import ist_gueltige_ahv, normalisiere_ahv

# Die Beispielnummern sind erfunden bzw. selbst berechnet und keine echten Personendaten.
# Pruefziffer-Beispiele (Gewichte 1,3,1,3,... ueber die ersten 12 Ziffern):
#   "7561234567897": Summe 7+15+6+3+2+9+4+15+6+21+8+27 = 123 -> Pruefziffer (10-3)%10 = 7
#   "7569217076985": Summe 7+15+6+27+2+3+7+0+7+18+9+24 = 125 -> Pruefziffer (10-5)%10 = 5


@pytest.mark.parametrize(
    "wert",
    [
        "756.1234.5678.97",
        "7561234567897",
        "756 1234 5678 97",
        "756-9217-0769-85",
    ],
)
def test_ist_gueltige_ahv_akzeptiert_gueltige_schreibweisen(wert):
    assert ist_gueltige_ahv(wert) is True


@pytest.mark.parametrize(
    "wert",
    [
        "756.1234.5678.98",  # falsche Pruefziffer
        "755.1234.5678.97",  # falsches Praefix
        "756123456789",  # 12 Ziffern
        "75612345678971",  # 14 Ziffern
        "756.1234.5678.9A",  # Buchstabe
        "",
        "756.1234.5678.9٣",  # Nicht-ASCII-Ziffer
    ],
)
def test_ist_gueltige_ahv_lehnt_ungueltige_eingaben_ab(wert):
    assert ist_gueltige_ahv(wert) is False


def test_ist_gueltige_ahv_akzeptiert_gemischte_trennzeichen():
    assert ist_gueltige_ahv(" 756. 1234-5678 97 ") is True


def test_ist_gueltige_ahv_wirft_bei_nicht_text_eingabe_nicht():
    assert ist_gueltige_ahv(None) is False


@pytest.mark.parametrize(
    ("wert", "erwartet"),
    [
        ("7561234567897", "756.1234.5678.97"),
        (" 756.1234.5678.97 ", "756.1234.5678.97"),
        ("756 1234 5678 97", "756.1234.5678.97"),
        ("756-9217-0769-85", "756.9217.0769.85"),
    ],
)
def test_normalisiere_ahv_erzeugt_standardschreibweise(wert, erwartet):
    assert normalisiere_ahv(wert) == erwartet


@pytest.mark.parametrize(
    "wert",
    [
        "756.1234.5678.98",
        "755.1234.5678.97",
        "756123456789",
        "75612345678971",
        "756.1234.5678.9A",
        "",
        "756.1234.5678.9٣",
    ],
)
def test_normalisiere_ahv_wirft_bei_ungueltiger_eingabe(wert):
    with pytest.raises(ValueError):
        normalisiere_ahv(wert)


@pytest.mark.parametrize(
    "wert",
    [
        "756.1234.5678.97",
        "7561234567897",
        "756 1234 5678 97",
        "756-9217-0769-85",
        "756.1234.5678.98",
        "756123456789",
        "",
        "abc",
    ],
)
def test_ist_gueltig_genau_dann_wenn_normalisieren_klappt(wert):
    try:
        normalisiere_ahv(wert)
    except ValueError:
        assert ist_gueltige_ahv(wert) is False
    else:
        assert ist_gueltige_ahv(wert) is True

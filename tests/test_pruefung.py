from dataclasses import FrozenInstanceError

import pytest

from chimport.pruefung import Fehler, normalisiere_zeilen, pruefe_zeilen

# Alle Testwerte sind erfunden bzw. selbst berechnet und keine echten Personendaten.

SCHEMA = {
    "plz": "plz",
    "ahv": "ahv",
    "datum": "datum",
    "betrag": "betrag",
    "telefon": "telefon",
    "bemerkung": "text",
}


def test_pruefe_zeilen_meldet_fehlende_werte_in_reihenfolge() -> None:
    zeilen = [
        {
            "bemerkung": "gueltig",
            "telefon": "079 123 45 67",
            "betrag": "CHF 1'234.5",
            "datum": "29.02.2024",
            "ahv": "756.1234.5678.97",
            "plz": "CH-8001",
        },
        {
            "plz": "999",
            "ahv": "756.9217.0769.85",
            "datum": "31.04.2024",
            "betrag": "12.00",
            "telefon": "+49 30 123456",
            "bemerkung": "ungueltig",
        },
        {
            "plz": "3000",
            "ahv": "756.1234.5678.98",
            "datum": "2024-01-01",
            "betrag": "1,50",
            "telefon": "031 123 45 67",
            "bemerkung": "gemischt",
        },
    ]

    assert pruefe_zeilen(zeilen, SCHEMA) == [
        Fehler(zeile=3, spalte="plz", wert="999", typ="plz"),
        Fehler(zeile=3, spalte="datum", wert="31.04.2024", typ="datum"),
        Fehler(zeile=3, spalte="telefon", wert="+49 30 123456", typ="telefon"),
        Fehler(zeile=4, spalte="ahv", wert="756.1234.5678.98", typ="ahv"),
        Fehler(zeile=4, spalte="betrag", wert="1,50", typ="betrag"),
    ]


def test_pruefe_zeilen_ohne_fehler() -> None:
    zeilen = [
        {
            "plz": "  CH-8001 ",
            "ahv": "756 1234 5678 97",
            "datum": "1.3.2023",
            "betrag": "chf 1'234.5",
            "telefon": "0041 79 123 45 67",
            "bemerkung": "  Text  ",
        }
    ]

    assert pruefe_zeilen(zeilen, SCHEMA) == []


def test_leere_werte_sind_erlaubt_und_werden_zu_leerem_text() -> None:
    schema = {
        "plz": "plz",
        "ahv": "ahv",
        "datum": "datum",
        "betrag": "betrag",
        "telefon": "telefon",
        "bemerkung": "text",
    }
    zeile = {
        "plz": "",
        "ahv": "   ",
        "datum": "\t",
        "betrag": "\n",
        "telefon": "  ",
        "bemerkung": " \t ",
    }
    zeilen = [dict(zeile)]

    assert pruefe_zeilen(zeilen, schema) == []
    assert normalisiere_zeilen(zeilen, schema) == [{spalte: "" for spalte in schema}]
    assert zeilen == [zeile]


def test_normalisiere_zeilen_acceptance_beispiel() -> None:
    zeilen = [{"plz": "CH-8001", "betrag": "CHF 1'234.5"}]
    vorher = [dict(zeile) for zeile in zeilen]

    ergebnis = normalisiere_zeilen(zeilen, {"plz": "plz", "betrag": "betrag"})

    assert ergebnis == [{"plz": "8001", "betrag": "1234.50"}]
    assert zeilen == vorher
    assert ergebnis[0] is not zeilen[0]


def test_normalisiere_zeilen_alle_typen_und_fremde_spalten() -> None:
    zeilen = [
        {
            "plz": " ch-8001 ",
            "ahv": "756 1234 5678 97",
            "datum": "1.3.2023",
            "betrag": "chf 1'234.5",
            "telefon": "0041 79 123 45 67",
            "bemerkung": "  Beispiel  ",
            "frei": "  bleibt unveraendert  ",
        }
    ]

    ergebnis = normalisiere_zeilen(zeilen, SCHEMA)

    assert ergebnis == [
        {
            "plz": "8001",
            "ahv": "756.1234.5678.97",
            "datum": "2023-03-01",
            "betrag": "1234.50",
            "telefon": "+41 79 123 45 67",
            "bemerkung": "Beispiel",
            "frei": "  bleibt unveraendert  ",
        }
    ]
    assert zeilen[0]["plz"] == " ch-8001 "
    assert zeilen[0]["bemerkung"] == "  Beispiel  "


def test_spalten_ausserhalb_des_schemas_werden_ignoriert() -> None:
    zeilen = [{"plz": "8001", "frei": "112"}]

    assert pruefe_zeilen(zeilen, {"plz": "plz"}) == []
    assert normalisiere_zeilen(zeilen, {"plz": "plz"}) == [{"plz": "8001", "frei": "112"}]


@pytest.mark.parametrize("funktion", [pruefe_zeilen, normalisiere_zeilen])
def test_unbekannter_typ_wirft_valueerror(funktion) -> None:
    with pytest.raises(ValueError):
        funktion([], {"plz": "zahl"})


@pytest.mark.parametrize("funktion", [pruefe_zeilen, normalisiere_zeilen])
def test_fehlende_schemaspalte_wirft_valueerror(funktion) -> None:
    with pytest.raises(ValueError):
        funktion([{"plz": "8001"}], {"plz": "plz", "datum": "datum"})


def test_ungueltiger_wert_wirft_bei_normalisierung_valueerror() -> None:
    with pytest.raises(ValueError):
        normalisiere_zeilen([{"plz": "999"}], {"plz": "plz"})


def test_leere_zeilenliste() -> None:
    assert pruefe_zeilen([], {"plz": "plz"}) == []
    assert normalisiere_zeilen([], {"plz": "plz"}) == []


def test_fehler_ist_unveraenderlich() -> None:
    fehler = Fehler(zeile=2, spalte="plz", wert="999", typ="plz")

    with pytest.raises(FrozenInstanceError):
        fehler.zeile = 3

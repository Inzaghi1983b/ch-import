import pytest

from chimport.csvlesen import lese_csv, lese_csv_mit_kopf


def test_semikolon_und_cp1252(tmp_path):
    pfad = tmp_path / "orte.csv"
    pfad.write_bytes("PLZ;Ort\r\n8000;Zürich\r\n".encode("cp1252"))

    assert lese_csv(pfad) == [{"PLZ": "8000", "Ort": "Zürich"}]


def test_komma_und_utf8_bom(tmp_path):
    pfad = tmp_path / "personen.csv"
    pfad.write_bytes(b"\xef\xbb\xbfName,Vorname\r\nMeier,Anna\r\n")

    assert lese_csv(pfad) == [{"Name": "Meier", "Vorname": "Anna"}]


def test_tabulator(tmp_path):
    pfad = tmp_path / "betraege.csv"
    pfad.write_text("Name\tBetrag\nMeier\t12.50\n", encoding="utf-8")

    assert lese_csv(pfad) == [{"Name": "Meier", "Betrag": "12.50"}]


def test_anfuehrungszeichen_mit_trennzeichen(tmp_path):
    pfad = tmp_path / "notiz.csv"
    pfad.write_text('PLZ;Bemerkung\n8000;"Zuerich; naehe Grenze"\n', encoding="utf-8")

    assert lese_csv(pfad) == [{"PLZ": "8000", "Bemerkung": "Zuerich; naehe Grenze"}]


def test_leere_zeilen_zwischendurch_werden_uebersprungen(tmp_path):
    pfad = tmp_path / "liste.csv"
    pfad.write_text("PLZ;Ort\n\n8000;Zuerich\n\n\n9000;St. Gallen\n", encoding="utf-8")

    assert lese_csv(pfad) == [
        {"PLZ": "8000", "Ort": "Zuerich"},
        {"PLZ": "9000", "Ort": "St. Gallen"},
    ]


def test_kopfzeilen_werden_getrimmt_werte_nicht(tmp_path):
    pfad = tmp_path / "roh.csv"
    pfad.write_text(" PLZ ; Ort \n8000; Zuerich \n", encoding="utf-8")

    assert lese_csv(pfad) == [{"PLZ": "8000", "Ort": " Zuerich "}]


def test_semikolon_gewinnt_bei_gleichstand(tmp_path):
    pfad = tmp_path / "gleichstand.csv"
    pfad.write_text("a,b;c\n1,2;3\n", encoding="utf-8")

    assert lese_csv(pfad) == [{"a,b": "1,2", "c": "3"}]


def test_pfad_als_string(tmp_path):
    pfad = tmp_path / "ort.csv"
    pfad.write_text("PLZ;Ort\n8000;Zuerich\n", encoding="utf-8")

    assert lese_csv(str(pfad)) == [{"PLZ": "8000", "Ort": "Zuerich"}]


def test_datei_nur_mit_kopfzeile(tmp_path):
    pfad = tmp_path / "leer.csv"
    pfad.write_text("PLZ;Ort\n", encoding="utf-8")

    assert lese_csv(pfad) == []


def test_doppelte_spaltennamen(tmp_path):
    pfad = tmp_path / "doppelt.csv"
    pfad.write_text("PLZ; PLZ \n8000;9000\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Zeile 1"):
        lese_csv(pfad)


def test_leere_datei(tmp_path):
    pfad = tmp_path / "leer.csv"
    pfad.write_bytes(b"")

    with pytest.raises(ValueError, match="Zeile 1"):
        lese_csv(pfad)


def test_datei_nur_aus_leeren_zeilen(tmp_path):
    pfad = tmp_path / "nur_leer.csv"
    pfad.write_text("\n\n\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Zeile 1"):
        lese_csv(pfad)


def test_falsche_spaltenzahl(tmp_path):
    pfad = tmp_path / "kaputt.csv"
    pfad.write_text("PLZ;Ort\n8000;Zuerich\n9000\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Zeile 3"):
        lese_csv(pfad)


def test_lese_csv_mit_kopf_liefert_spaltennamen_und_zeilen(tmp_path):
    datei = tmp_path / "a.csv"
    datei.write_text(" name ; ort \nA;Bern\n", encoding="utf-8")
    spalten, zeilen = lese_csv_mit_kopf(datei)
    assert spalten == ["name", "ort"]
    assert zeilen == [{"name": "A", "ort": "Bern"}]


def test_lese_csv_mit_kopf_ohne_datenzeilen_behaelt_kopfzeile(tmp_path):
    datei = tmp_path / "b.csv"
    datei.write_text("a;b\n", encoding="utf-8")
    assert lese_csv_mit_kopf(datei) == (["a", "b"], [])

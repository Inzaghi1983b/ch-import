"""CSV-Dateien mit Schweizer Eigenheiten einlesen.

Regeln (Quelle: RFC 4180, https://www.rfc-editor.org/rfc/rfc4180 sowie die
Projektvorgabe zur Kodierung):

* Kodierung: zuerst UTF-8 (mit oder ohne BOM), schlaegt das fehl, Windows-1252
  (CP1252).
* Trennzeichen wird anhand der Kopfzeile unter ``;``, ``,`` und Tab erkannt;
  bei Gleichstand gewinnt das Semikolon.
* Anfuehrungszeichen folgen RFC 4180 (``csv``-Modul).
* Erste nicht leere Zeile ist die Kopfzeile; Spaltennamen werden von
  Leerzeichen am Rand befreit, Werte bleiben unveraendert.
* Komplett leere Zeilen werden uebersprungen. Doppelte Spaltennamen, leere
  Datei oder eine Zeile mit anderer Spaltenzahl als die Kopfzeile loesen
  ``ValueError`` mit der Zeilennummer (1-basiert, Kopfzeile = Zeile 1) aus.
"""

import csv
import io
from pathlib import Path

_TRENNZEICHEN = (";", ",", "\t")


def _dekodiere(daten: bytes) -> str:
    """Dekodiere Rohdaten als UTF-8 (mit oder ohne BOM), sonst als CP1252."""
    try:
        return daten.decode("utf-8-sig")
    except UnicodeDecodeError:
        return daten.decode("cp1252")


def _anzahl_spalten(zeile: str, trennzeichen: str) -> int:
    """Anzahl Spalten, die ein CSV-Leser fuer ``zeile`` liefert."""
    try:
        return len(next(csv.reader([zeile], delimiter=trennzeichen)))
    except (csv.Error, StopIteration):
        return 0


def _erkenne_trennzeichen(kopfzeile: str) -> str:
    """Erkenne das Trennzeichen der Kopfzeile; bei Gleichstand gewinnt ``;``."""
    anzahl = {zeichen: _anzahl_spalten(kopfzeile, zeichen) for zeichen in _TRENNZEICHEN}
    beste = max(anzahl.values())
    for zeichen in _TRENNZEICHEN:
        if anzahl[zeichen] == beste:
            return zeichen
    return _TRENNZEICHEN[0]


def _erste_nicht_leere_zeile(text: str) -> str | None:
    """Erste nicht leere Zeile des Textes oder ``None``, wenn es keine gibt."""
    for zeile in text.splitlines():
        if zeile != "":
            return zeile
    return None


def lese_csv(pfad: str | Path) -> list[dict[str, str]]:
    """Lies eine CSV-Datei und gib die Datenzeilen als Liste von Dicts zurueck.

    Die erste nicht leere Zeile ist die Kopfzeile und liefert die Schluessel.
    Spaltennamen werden von Leerzeichen am Rand befreit, Werte bleiben
    unveraendert. Komplett leere Zeilen werden uebersprungen.

    :param pfad: Pfad zur CSV-Datei.
    :returns: Eine Liste von Dicts (Spaltenname -> Wert) in Dateireihenfolge.
    :raises ValueError: Bei doppelten Spaltennamen, leerer Datei oder einer
        Zeile mit anderer Spaltenzahl als die Kopfzeile. Die Meldung enthaelt
        die 1-basierte Zeilennummer (Kopfzeile = Zeile 1).
    """
    text = _dekodiere(Path(pfad).read_bytes())
    kopfzeile = _erste_nicht_leere_zeile(text)
    if kopfzeile is None:
        raise ValueError("Leere Datei: keine Kopfzeile in Zeile 1")
    trennzeichen = _erkenne_trennzeichen(kopfzeile)

    ergebnis: list[dict[str, str]] = []
    spalten: list[str] = []
    leser = csv.reader(io.StringIO(text), delimiter=trennzeichen)
    for zeile in leser:
        if zeile == []:
            continue
        if not spalten:
            spalten = [name.strip() for name in zeile]
            doppelte = sorted({name for name in spalten if spalten.count(name) > 1})
            if doppelte:
                raise ValueError(
                    f"Zeile {leser.line_num}: doppelte Spaltennamen: {', '.join(doppelte)}"
                )
            continue
        if len(zeile) != len(spalten):
            raise ValueError(f"Zeile {leser.line_num}: {len(zeile)} Spalten statt {len(spalten)}")
        ergebnis.append(dict(zip(spalten, zeile, strict=True)))
    if not spalten:
        raise ValueError("Leere Datei: keine Kopfzeile in Zeile 1")
    return ergebnis

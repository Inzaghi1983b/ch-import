"""Zeilenweise Pruefung und Normalisierung von CSV-Daten anhand eines Schemas.

Regel (Quelle: Issue #7 dieses Repositories): Ein Schema ordnet jedem Spaltennamen
einen Typ zu. Erlaubte Typen sind ``plz``, ``ahv``, ``datum``, ``betrag``,
``telefon`` und ``text``. Die Pruefung und Normalisierung verwendet die jeweils
zustaendigen Module dieses Pakets, damit die fachlichen Regeln nur an einer Stelle
definiert sind. Leere Werte (auch reine Leerzeichen) sind fuer jeden Typ erlaubt.
Die erste Datenzeile hat die Zeilennummer 2, weil die Kopfzeile die Zeile 1 ist.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from chimport.ahv import ist_gueltige_ahv, normalisiere_ahv
from chimport.betrag import ist_gueltiger_betrag, normalisiere_betrag
from chimport.datum import ist_gueltiges_datum, normalisiere_datum
from chimport.plz import ist_gueltige_plz, normalisiere_plz
from chimport.telefon import ist_gueltige_telefonnummer, normalisiere_telefonnummer


@dataclass(frozen=True)
class Fehler:
    """Ein ungueltiger Wert in einer Datenzeile.

    :param zeile: 1-basierte Zeilennummer in der Datei (erste Datenzeile = 2).
    :param spalte: Spaltenname aus dem Schema.
    :param wert: Der unveraenderte, ungueltige Wert.
    :param typ: Der im Schema angegebene Typ der Spalte.
    """

    zeile: int
    spalte: str
    wert: str
    typ: str


def _ist_text(wert: str) -> bool:
    """Textwerte sind immer gueltig; die Leerpruefung erfolgt davor."""
    return True


def _normalisiere_text(wert: str) -> str:
    """Entfernt fuehrende und nachfolgende Leerzeichen von einem Textwert."""
    if not isinstance(wert, str):
        raise ValueError(f"Ungueltiger Text: {wert!r}")
    return wert.strip()


_PRUEFUNGEN: dict[str, Callable[[str], bool]] = {
    "plz": ist_gueltige_plz,
    "ahv": ist_gueltige_ahv,
    "datum": ist_gueltiges_datum,
    "betrag": ist_gueltiger_betrag,
    "telefon": ist_gueltige_telefonnummer,
    "text": _ist_text,
}

_NORMALISIERUNGEN: dict[str, Callable[[str], str]] = {
    "plz": normalisiere_plz,
    "ahv": normalisiere_ahv,
    "datum": normalisiere_datum,
    "betrag": normalisiere_betrag,
    "telefon": normalisiere_telefonnummer,
    "text": _normalisiere_text,
}


def _pruefe_schema(schema: dict[str, str]) -> None:
    """Stellt sicher, dass jeder im Schema genannte Typ bekannt ist."""
    for spalte, typ in schema.items():
        if typ not in _PRUEFUNGEN:
            raise ValueError(f"Unbekannter Typ {typ!r} fuer Spalte {spalte!r}")


def _pruefe_spalten(zeile: dict[str, str], schema: dict[str, str], zeilennummer: int) -> None:
    """Stellt sicher, dass alle im Schema genannten Spalten in der Zeile vorkommen."""
    fehlend = [spalte for spalte in schema if spalte not in zeile]
    if fehlend:
        raise ValueError(f"Zeile {zeilennummer}: fehlende Spalte(n): {', '.join(fehlend)}")


def _ist_leer(wert: str) -> bool:
    """Prueft, ob ein Wert nach dem Trimmen leer ist."""
    return isinstance(wert, str) and wert.strip() == ""


def pruefe_zeilen(zeilen: list[dict[str, str]], schema: dict[str, str]) -> list[Fehler]:
    """Prueft alle Zeilen gegen das Schema und liefert die gefundenen Fehler.

    Die Reihenfolge der Fehler ist nach Zeile und innerhalb einer Zeile nach der
    Reihenfolge der Spalten im Schema. Leere Werte werden nicht gemeldet.

    :param zeilen: Datenzeilen als Dicts (Spaltenname -> Wert).
    :param schema: Spaltenname -> Typ (``plz``, ``ahv``, ``datum``, ``betrag``,
        ``telefon`` oder ``text``).
    :returns: Liste der ungueltigen Werte.
    :raises ValueError: Bei einem unbekannten Typ oder einer im Schema genannten
        Spalte, die in einer Zeile fehlt.
    """
    _pruefe_schema(schema)
    for index, zeile in enumerate(zeilen):
        _pruefe_spalten(zeile, schema, index + 2)

    fehler: list[Fehler] = []
    for index, zeile in enumerate(zeilen):
        zeilennummer = index + 2
        for spalte, typ in schema.items():
            wert = zeile[spalte]
            if _ist_leer(wert):
                continue
            if not _PRUEFUNGEN[typ](wert):
                fehler.append(Fehler(zeile=zeilennummer, spalte=spalte, wert=wert, typ=typ))
    return fehler


def normalisiere_zeilen(
    zeilen: list[dict[str, str]], schema: dict[str, str]
) -> list[dict[str, str]]:
    """Normalisiert alle Zeilen gemaess Schema, ohne die Eingabe zu veraendern.

    Es werden neue Dicts zurueckgegeben. Spalten ausserhalb des Schemas bleiben
    unveraendert. Leere Werte werden zu ``""``; Textwerte werden von Leerzeichen
    am Rand befreit.

    :param zeilen: Datenzeilen als Dicts (Spaltenname -> Wert).
    :param schema: Spaltenname -> Typ (``plz``, ``ahv``, ``datum``, ``betrag``,
        ``telefon`` oder ``text``).
    :returns: Neue Liste mit normalisierten Dicts.
    :raises ValueError: Bei einem unbekannten Typ, einer fehlenden Schemaspalte
        oder einem ungueltigen Wert.
    """
    _pruefe_schema(schema)
    ergebnis: list[dict[str, str]] = []
    for index, zeile in enumerate(zeilen):
        zeilennummer = index + 2
        _pruefe_spalten(zeile, schema, zeilennummer)
        normalisiert = dict(zeile)
        for spalte, typ in schema.items():
            wert = zeile[spalte]
            if _ist_leer(wert):
                normalisiert[spalte] = ""
                continue
            try:
                normalisiert[spalte] = _NORMALISIERUNGEN[typ](wert)
            except ValueError as fehler:
                raise ValueError(f"Zeile {zeilennummer}, Spalte {spalte!r}: {fehler}") from fehler
        ergebnis.append(normalisiert)
    return ergebnis

"""Kommandozeile fuer Pruefung und Normalisierung von CSV-Dateien.

Regel (Quelle: Issue #8 dieses Repositories): Die Befehle ``pruefe`` und
``normalisiere`` lesen eine CSV-Datei gemaess ``csvlesen.lese_csv`` und wenden
das Schema aus ``pruefung.py`` an. Ausgaben von ``normalisiere`` sind UTF-8 mit
Semikolon als Trennzeichen und der Kopfzeile der Eingabe. Exit-Codes: 0 ohne
Fehler, 1 bei Pruefungsfehlern, 2 bei Aufruf-, Schema- oder Dateifehlern.
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

from chimport.csvlesen import (
    _dekodiere,
    _erkenne_trennzeichen,
    _erste_nicht_leere_zeile,
    lese_csv,
)
from chimport.pruefung import Fehler, normalisiere_zeilen, pruefe_zeilen


def _parse_schema(text: str) -> dict[str, str]:
    """Zerlegt ``Spalte=typ,Spalte=typ`` in ein Schema-Dict.

    :raises ValueError: Bei einem leeren oder ungueltigen Eintrag sowie bei
        einer doppelt genannten Spalte.
    """
    schema: dict[str, str] = {}
    for eintrag in text.split(","):
        spalte, trenner, typ = eintrag.partition("=")
        spalte = spalte.strip()
        typ = typ.strip()
        if not trenner or not spalte or not typ:
            raise ValueError(f"Ungueltiger Schema-Eintrag: {eintrag!r}")
        if spalte in schema:
            raise ValueError(f"Doppelte Spalte im Schema: {spalte!r}")
        schema[spalte] = typ
    return schema


def _formatiere_fehler(fehler: Fehler) -> str:
    """Liefert die Ausgabezeile fuer einen Pruefungsfehler."""
    return (
        f"Zeile {fehler.zeile}, Spalte {fehler.spalte}: "
        f'"{fehler.wert}" ist keine gueltige {fehler.typ}'
    )


def _kopfzeile(pfad: str | Path) -> list[str]:
    """Liest die getrimmten Spaltennamen der Kopfzeile einer CSV-Datei."""
    text = _dekodiere(Path(pfad).read_bytes())
    kopfzeile = _erste_nicht_leere_zeile(text)
    if kopfzeile is None:
        raise ValueError("Leere Datei: keine Kopfzeile in Zeile 1")
    trennzeichen = _erkenne_trennzeichen(kopfzeile)
    return [name.strip() for name in next(csv.reader([kopfzeile], delimiter=trennzeichen))]


def _als_csv(spalten: list[str], zeilen: list[dict[str, str]]) -> str:
    """Serialisiert Zeilen als CSV mit Semikolon und Kopfzeile."""
    puffer = io.StringIO()
    schreiber = csv.writer(puffer, delimiter=";", lineterminator="\n")
    schreiber.writerow(spalten)
    for zeile in zeilen:
        schreiber.writerow([zeile[spalte] for spalte in spalten])
    return puffer.getvalue()


def _pruefe(pfad: str, schema: dict[str, str]) -> int:
    """Fuehrt den Befehl ``pruefe`` aus und liefert den Exit-Code."""
    fehler = pruefe_zeilen(lese_csv(pfad), schema)
    for eintrag in fehler:
        print(_formatiere_fehler(eintrag))
    return 1 if fehler else 0


def _normalisiere(pfad: str, schema: dict[str, str], ausgabe: str | None) -> int:
    """Fuehrt den Befehl ``normalisiere`` aus und liefert den Exit-Code."""
    zeilen = lese_csv(pfad)
    fehler = pruefe_zeilen(zeilen, schema)
    if fehler:
        for eintrag in fehler:
            print(_formatiere_fehler(eintrag))
        return 1

    spalten = _kopfzeile(pfad)
    inhalt = _als_csv(spalten, normalisiere_zeilen(zeilen, schema))
    if ausgabe is None:
        sys.stdout.write(inhalt)
    else:
        Path(ausgabe).write_text(inhalt, encoding="utf-8", newline="")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Verarbeitet die Kommandozeile und liefert den Exit-Code.

    :param argv: Argumente ohne Programmnamen; ``None`` verwendet ``sys.argv``.
    :returns: 0 ohne Fehler, 1 bei Pruefungsfehlern, 2 bei Aufruf- oder
        Dateifehlern.
    """
    parser = argparse.ArgumentParser(prog="python -m chimport")
    unterbefehle = parser.add_subparsers(dest="befehl", required=True)

    pruefe_parser = unterbefehle.add_parser("pruefe", help="CSV-Datei pruefen")
    pruefe_parser.add_argument("datei", metavar="DATEI")
    pruefe_parser.add_argument("--schema", required=True, metavar="SCHEMA")

    normalisiere_parser = unterbefehle.add_parser(
        "normalisiere", help="CSV-Datei pruefen und normalisieren"
    )
    normalisiere_parser.add_argument("datei", metavar="DATEI")
    normalisiere_parser.add_argument("--schema", required=True, metavar="SCHEMA")
    normalisiere_parser.add_argument("--ausgabe", metavar="AUSGABE")

    try:
        args = parser.parse_args(argv)
    except SystemExit as fehler:
        return int(fehler.code) if fehler.code is not None else 2

    try:
        schema = _parse_schema(args.schema)
        if args.befehl == "pruefe":
            return _pruefe(args.datei, schema)
        return _normalisiere(args.datei, schema, args.ausgabe)
    except (OSError, ValueError, csv.Error) as fehler:
        print(f"Fehler: {fehler}", file=sys.stderr)
        return 2

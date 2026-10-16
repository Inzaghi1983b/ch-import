"""Datum: prueft und normalisiert Datumsangaben nach Schweizer Konvention.

Regel und Quelle: In der Schweiz wird das Datum als ``TT.MM.JJJJ`` geschrieben
(Tag und Monat ein- oder zweistellig, Jahr vierstellig); die ISO-Norm ISO 8601
verwendet ``JJJJ-MM-TT``. Akzeptiert wird nur ein reales Kalenderdatum (mit
Schaltjahren) zwischen 1900 und 2100. Als Ziffern zaehlen nur ASCII-Ziffern
``0-9``.
"""

import datetime
import re

_MUSTER_PUNKT = re.compile(r"([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})\Z", re.ASCII)
_MUSTER_ISO = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})\Z", re.ASCII)

_MIN_JAHR = 1900
_MAX_JAHR = 2100


def _zerlege(wert: str) -> tuple[int, int, int] | None:
    """Zerlegt einen Datumstext in Tag, Monat und Jahr oder gibt ``None`` zurueck."""
    if not isinstance(wert, str):
        return None
    text = wert.strip()
    treffer = _MUSTER_PUNKT.fullmatch(text)
    if treffer is not None:
        tag, monat, jahr = treffer.groups()
    else:
        treffer = _MUSTER_ISO.fullmatch(text)
        if treffer is None:
            return None
        jahr, monat, tag = treffer.groups()
    return int(tag), int(monat), int(jahr)


def _ist_reales_datum(tag: int, monat: int, jahr: int) -> bool:
    """Prueft, ob Tag, Monat und Jahr ein reales Datum im erlaubten Bereich bilden."""
    if not _MIN_JAHR <= jahr <= _MAX_JAHR:
        return False
    try:
        datetime.date(jahr, monat, tag)
    except ValueError:
        return False
    return True


def ist_gueltiges_datum(wert: str) -> bool:
    """Prueft, ob ``wert`` ein gueltiges Datum ist (wirft nie eine Ausnahme).

    Gueltig sind ``TT.MM.JJJJ`` (Tag und Monat ein- oder zweistellig, Jahr
    vierstellig) und ISO ``JJJJ-MM-TT`` mit einem realen Kalenderdatum zwischen
    1900 und 2100.
    """
    zerlegt = _zerlege(wert)
    if zerlegt is None:
        return False
    return _ist_reales_datum(*zerlegt)


def normalisiere_datum(wert: str) -> str:
    """Gibt das Datum in ISO-Schreibweise ``JJJJ-MM-TT`` zurueck.

    Loest ``ValueError`` aus, wenn ``wert`` kein gueltiges Datum ist.
    """
    zerlegt = _zerlege(wert)
    if zerlegt is None or not _ist_reales_datum(*zerlegt):
        raise ValueError(f"Ungueltiges Datum: {wert!r}")
    tag, monat, jahr = zerlegt
    return f"{jahr:04d}-{monat:02d}-{tag:02d}"

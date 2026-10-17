"""Pruefung und Normalisierung von Schweizer und liechtensteinischen PLZ.

Regel: Eine PLZ besteht aus genau vier ASCII-Ziffern im Bereich 1000 bis 9658.
Optional steht davor der Laenderpraefix ``CH-`` oder ``FL-`` (gross oder klein);
Leerzeichen am Rand werden ignoriert.

Quelle: Post CH, PLZ-Verzeichnis.
"""

ASCII_ZIFFERN = frozenset("0123456789")
LANDESPRAEFIXE = ("ch-", "fl-")
PLZ_MIN = 1000
PLZ_MAX = 9658
PLZ_LAENGE = 4


def _plz_ziffern(wert: str) -> str | None:
    """Gibt die vier Ziffern der PLZ zurueck, sonst ``None``."""
    if not isinstance(wert, str):
        return None

    text = wert.strip()
    klein = text.lower()
    for praefix in LANDESPRAEFIXE:
        if klein.startswith(praefix):
            text = text[len(praefix) :]
            break

    if len(text) != PLZ_LAENGE:
        return None
    if any(zeichen not in ASCII_ZIFFERN for zeichen in text):
        return None
    if not PLZ_MIN <= int(text) <= PLZ_MAX:
        return None
    return text


def ist_gueltige_plz(wert: str) -> bool:
    """Prueft, ob *wert* eine gueltige PLZ ist.

    wirft bei ungueltiger Eingabe keine Ausnahme.
    """
    return _plz_ziffern(wert) is not None


def normalisiere_plz(wert: str) -> str:
    """Gibt die PLZ in der Standardschreibweise zurueck: vier Ziffern.

    Beispiel: ``"CH-8001"`` wird zu ``"8001"``. Loest bei ungueltiger Eingabe
    ``ValueError`` aus.
    """
    ziffern = _plz_ziffern(wert)
    if ziffern is None:
        raise ValueError(f"Ungueltige PLZ: {wert!r}")
    return ziffern

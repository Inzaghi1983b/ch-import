"""Jahr: prueft Jahreszahlen im Bereich 1900 bis 2100.

Regel (Quelle: Issue #36 dieses Repositories): Gueltig sind genau vier
ASCII-Ziffern ``0-9`` mit einem Wert von 1900 bis 2100. Leerraum am Rand wird
ignoriert. Andere Ziffern, etwa arabisch-indische, zaehlen nicht.
"""

ASCII_ZIFFERN = frozenset("0123456789")
JAHR_MIN = 1900
JAHR_MAX = 2100
JAHR_LAENGE = 4


def ist_jahr(wert: str) -> bool:
    """Prueft, ob ``wert`` eine gueltige Jahreszahl ist (wirft nie eine Ausnahme).

    Gueltig sind genau vier ASCII-Ziffern mit einem Wert von 1900 bis 2100;
    Leerraum am Rand wird ignoriert.
    """
    if not isinstance(wert, str):
        return False

    text = wert.strip()
    if len(text) != JAHR_LAENGE:
        return False
    if any(zeichen not in ASCII_ZIFFERN for zeichen in text):
        return False
    return JAHR_MIN <= int(text) <= JAHR_MAX

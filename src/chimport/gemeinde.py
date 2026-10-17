"""Pruefung von Schweizer BFS-Gemeindenummern.

Regel (Quelle: Bundesamt fuer Statistik (BFS), Gemeindeverzeichnis der Schweiz):
Eine BFS-Gemeindenummer besteht aus 1 bis 4 ASCII-Ziffern ``0-9`` mit einem Wert
von 1 bis 9999. Leerraum ist nicht zulaessig. Es zaehlen nur ASCII-Ziffern.
"""

ASCII_ZIFFERN = frozenset("0123456789")
BFS_MIN = 1
BFS_MAX = 9999
BFS_MAX_LAENGE = 4


def ist_bfs_nummer(wert: str) -> bool:
    """Prueft, ob ``wert`` eine gueltige BFS-Gemeindenummer ist.

    Gueltig sind 1 bis 4 ASCII-Ziffern mit einem Wert von 1 bis 9999, ohne
    Leerraum. Gibt ``bool`` zurueck und wirft bei ungueltiger Eingabe keine
    Ausnahme.
    """
    if not isinstance(wert, str):
        return False
    if not 1 <= len(wert) <= BFS_MAX_LAENGE:
        return False
    if any(zeichen not in ASCII_ZIFFERN for zeichen in wert):
        return False
    return BFS_MIN <= int(wert) <= BFS_MAX

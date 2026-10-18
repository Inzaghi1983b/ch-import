"""Laendercode: prueft Laendercodes im Format der Schweizer Importdaten.

Regel (Quelle: Issue #45 dieses Repositories): Gueltig sind ausschliesslich die
Grossbuchstaben-Codes ``CH``, ``DE``, ``FR``, ``IT``, ``AT`` und ``LI``. Eine
exakte Uebereinstimmung ist noetig; Leerraum am Rand macht den Code ungueltig.
"""

LAENDERCODES = frozenset({"CH", "DE", "FR", "IT", "AT", "LI"})


def ist_laendercode(wert: str) -> bool:
    """Prueft, ob ``wert`` ein unterstuetzter Laendercode ist.

    Gueltig sind genau ``CH``, ``DE``, ``FR``, ``IT``, ``AT`` und ``LI`` in
    Grossbuchstaben. Es wird kein Leerraum entfernt. Gibt bei jeder Eingabe
    ``bool`` zurueck und wirft nie eine Ausnahme.
    """
    if not isinstance(wert, str):
        return False
    return wert in LAENDERCODES

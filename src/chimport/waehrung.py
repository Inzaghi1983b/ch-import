"""Pruefung von Waehrungscodes.

Regel (Quelle: ISO 4217): Gueltig sind ausschliesslich die Grossbuchstaben-Codes
``CHF``, ``EUR``, ``USD`` und ``GBP``. Fuehrende und nachfolgende Leerzeichen
werden ignoriert.
"""

_WAEHRUNGEN = frozenset({"CHF", "EUR", "USD", "GBP"})


def ist_waehrung(wert: str) -> bool:
    """Prueft, ob ``wert`` ein unterstuetzter Waehrungscode ist.

    Fuehrende und nachfolgende Leerzeichen werden ignoriert. Gibt bei jeder
    Eingabe ``bool`` zurueck und wirft nie eine Ausnahme.
    """
    if not isinstance(wert, str):
        return False
    return wert.strip() in _WAEHRUNGEN

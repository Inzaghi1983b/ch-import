"""AHV-Nummer pruefen und normalisieren.

Regel (Quelle: GS1 General Specifications, Pruefziffernberechnung fuer GTIN/EAN-13;
eCH-0083 verwendet dieselbe EAN-13-Pruefziffer):
Die neue AHV-Nummer besteht aus 13 Ziffern, beginnt mit dem Praefix ``756`` und ist eine
EAN-13-Nummer. Ueber die ersten 12 Ziffern werden von links abwechselnd die Gewichte
1, 3, 1, 3, ... gelegt; die 13. Ziffer ist die Pruefziffer
``(10 - Summe % 10) % 10``.

Erlaubte Trennzeichen sind Punkt, Leerzeichen und Bindestrich (auch gemischt). Abgesehen von
diesen Trennzeichen sind nur ASCII-Ziffern ``0-9`` zulaessig. Standardschreibweise:
``756.XXXX.XXXX.XC``.
"""

_TRENNZEICHEN = ".- "
_PRAEFIX = "756"
_ZIFFERN = "0123456789"


def _ziffern(wert: str) -> str | None:
    """Trennzeichen entfernen; ``None`` zurueckgeben, wenn nur ASCII-Ziffern erlaubt sind."""
    if not isinstance(wert, str):
        return None
    rest = wert.strip()
    for zeichen in rest:
        if zeichen not in _ZIFFERN and zeichen not in _TRENNZEICHEN:
            return None
    ziffern = "".join(zeichen for zeichen in rest if zeichen in _ZIFFERN)
    return ziffern


def _pruefziffer(ziffern: str) -> int:
    """EAN-13-Pruefziffer aus den ersten 12 Ziffern berechnen."""
    summe = 0
    for index, zeichen in enumerate(ziffern[:12]):
        gewicht = 1 if index % 2 == 0 else 3
        summe += int(zeichen) * gewicht
    return (10 - summe % 10) % 10


def _ist_gueltig(ziffern: str | None) -> bool:
    """Ziffernfolge gegen Laenge, Praefix und Pruefziffer pruefen."""
    if ziffern is None or len(ziffern) != 13 or not ziffern.startswith(_PRAEFIX):
        return False
    return int(ziffern[12]) == _pruefziffer(ziffern)


def ist_gueltige_ahv(wert: str) -> bool:
    """Pruefen, ob ``wert`` eine gueltige neue AHV-Nummer ist.

    Gibt ``bool`` zurueck und wirft bei ungueltiger Eingabe nie eine Ausnahme.
    """
    return _ist_gueltig(_ziffern(wert))


def normalisiere_ahv(wert: str) -> str:
    """AHV-Nummer in die Standardschreibweise ``756.XXXX.XXXX.XC`` bringen.

    Loest bei ungueltiger Eingabe ``ValueError`` aus.
    """
    ziffern = _ziffern(wert)
    if not _ist_gueltig(ziffern):
        raise ValueError(f"Ungueltige AHV-Nummer: {wert!r}")
    assert ziffern is not None
    return f"{ziffern[:3]}.{ziffern[3:7]}.{ziffern[7:11]}.{ziffern[11:]}"

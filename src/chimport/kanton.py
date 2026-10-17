"""Pruefung und Normalisierung von Schweizer Kantonskuerzeln.

Regel: Gueltig sind die 26 offiziellen Kantonskuerzel AG AI AR BE BL BS FR GE
GL GR JU LU NE NW OW SG SH SO SZ TG TI UR VD VS ZG ZH. Gross- und
Kleinschreibung duerfen gemischt sein; Leerraum am Rand wird ignoriert. Die
Standardschreibweise sind Grossbuchstaben ohne Leerraum.

Quelle: Bundesamt fuer Statistik, offizielle Kantonskuerzel (ISO 3166-2:CH).
"""

KANTONE = frozenset(
    {
        "AG",
        "AI",
        "AR",
        "BE",
        "BL",
        "BS",
        "FR",
        "GE",
        "GL",
        "GR",
        "JU",
        "LU",
        "NE",
        "NW",
        "OW",
        "SG",
        "SH",
        "SO",
        "SZ",
        "TG",
        "TI",
        "UR",
        "VD",
        "VS",
        "ZG",
        "ZH",
    }
)


def _normalisiere(wert: str) -> str | None:
    """Gibt das Kantonskuerzel in Grossbuchstaben zurueck, sonst ``None``."""
    if not isinstance(wert, str):
        return None

    text = wert.strip().upper()
    if text not in KANTONE:
        return None
    return text


def ist_kanton(wert: str) -> bool:
    """Prueft, ob *wert* ein gueltiges Kantonskuerzel ist.

    Die Pruefung ignoriert Gross-/Kleinschreibung und Leerraum am Rand und
    wirft bei ungueltiger Eingabe keine Ausnahme.
    """
    return _normalisiere(wert) is not None


def normalisiere_kanton(wert: str) -> str:
    """Gibt das Kantonskuerzel in der Standardschreibweise zurueck.

    Beispiel: ``" zh "`` wird zu ``"ZH"``. Loest bei ungueltiger Eingabe
    ``ValueError`` aus.
    """
    kuerzel = _normalisiere(wert)
    if kuerzel is None:
        raise ValueError(f"Ungueltiges Kantonskuerzel: {wert!r}")
    return kuerzel

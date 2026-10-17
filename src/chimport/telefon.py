"""Pruefung und Normalisierung von Schweizer Telefonnummern.

Quelle der Regel: Nummerierungsplan der Schweiz nach E.164 (Bundesamt fuer
Kommunikation BAKOM). Die nationale Nummer besteht aus neun Ziffern, die erste
Ziffer liegt zwischen 2 und 9. Als Landesvorwahl sind "+41" und "0041" erlaubt,
national steht die Verkehrsausscheidungsziffer "0" am Anfang. Erlaubte
Trennzeichen sind Leerzeichen, "-", "/" und "." sowie Klammern um die
Ortskennzahl; direkt nach der Landesvorwahl ist zusaetzlich "(0)" erlaubt.
Es zaehlen nur ASCII-Ziffern "0" bis "9".
"""

_ASCII_ZIFFERN = frozenset("0123456789")
_TRENNZEICHEN = frozenset(" -/.")
_ERSTE_ZIFFERN = frozenset("23456789")


def _ziffern_aus_koerper(text: str) -> str | None:
    """Liest die Ziffern eines Nummernteils und prueft Trennzeichen und Klammern.

    Klammern muessen paarweise auftreten und mindestens eine Ziffer umschliessen.
    Bei unerlaubten Zeichen oder falscher Klammerung wird ``None`` zurueckgegeben.
    """
    ziffern: list[str] = []
    klammer_offen = False
    klammer_ziffern = 0
    for zeichen in text:
        if zeichen in _ASCII_ZIFFERN:
            ziffern.append(zeichen)
            if klammer_offen:
                klammer_ziffern += 1
        elif zeichen == "(":
            if klammer_offen:
                return None
            klammer_offen = True
            klammer_ziffern = 0
        elif zeichen == ")":
            if not klammer_offen or klammer_ziffern == 0:
                return None
            klammer_offen = False
        elif zeichen in _TRENNZEICHEN:
            continue
        else:
            return None
    if klammer_offen:
        return None
    return "".join(ziffern)


def _ohne_landesnull(text: str) -> str:
    """Entfernt ein optionales "(0)" direkt nach der Landesvorwahl."""
    rest = text.lstrip(" ")
    if rest.startswith("(0)"):
        return rest[3:]
    return rest


def _ohne_ortsklammer(text: str) -> str:
    """Loest ein Klammernpaar um die Ortskennzahl am Anfang, z.B. "(044) 123 45 67".

    Entfernt nur Klammern, die ausschliesslich ASCII-Ziffern umschliessen;
    andere Klammern bleiben stehen und werden spaeter als ungueltig erkannt.
    """
    if not text.startswith("("):
        return text
    ende = text.find(")")
    if ende == -1:
        return text
    inhalt = text[1:ende]
    if not inhalt or any(zeichen not in _ASCII_ZIFFERN for zeichen in inhalt):
        return text
    return text[1:ende] + text[ende + 1 :]


def _nationale_ziffern(wert: str) -> str | None:
    """Liefert die neun Ziffern der nationalen Nummer oder ``None``."""
    text = _ohne_ortsklammer(wert.strip())
    if not text:
        return None
    if text.startswith("+41"):
        koerper = _ohne_landesnull(text[3:])
    elif text.startswith("0041"):
        koerper = _ohne_landesnull(text[4:])
    elif text.startswith("0"):
        koerper = text[1:]
    else:
        return None
    ziffern = _ziffern_aus_koerper(koerper)
    if ziffern is None or len(ziffern) != 9 or ziffern[0] not in _ERSTE_ZIFFERN:
        return None
    return ziffern


def ist_gueltige_telefonnummer(wert: str) -> bool:
    """Prueft, ob ``wert`` eine gueltige Schweizer Telefonnummer ist.

    Gibt ``bool`` zurueck und wirft auch bei unbrauchbaren Eingaben (etwa
    Nicht-ASCII-Ziffern) keine Ausnahme.
    """
    try:
        normalisiere_telefonnummer(wert)
    except ValueError:
        return False
    return True


def normalisiere_telefonnummer(wert: str) -> str:
    """Gibt ``wert`` in der Standardschreibweise "+41 XX XXX XX XX" zurueck.

    Loest bei ungueltiger Eingabe ``ValueError`` aus.
    """
    ziffern = _nationale_ziffern(wert)
    if ziffern is None:
        raise ValueError(f"Ungueltige Telefonnummer: {wert!r}")
    return f"+41 {ziffern[0:2]} {ziffern[2:5]} {ziffern[5:7]} {ziffern[7:9]}"

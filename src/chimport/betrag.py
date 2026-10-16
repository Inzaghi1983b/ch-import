"""Pruefung und Normalisierung von CHF-Betraegen.

Regel (Quelle: Issue #4 dieses Repositories, gestuetzt auf die uebliche Schweizer
Schreibweise fuer Geldbetraege): Ein Betrag besteht aus einem optionalen ``CHF``
davor oder dahinter, einem optionalen Minus, einer Ziffernfolge mit optionalen
Tausendertrennern ``'`` oder ``’`` (nur in Dreiergruppen) und einem optionalen
Dezimalpunkt mit hoechstens zwei Nachkommastellen. Das Komma ist kein
Dezimaltrenner. Gerechnet wird ausschliesslich mit ``decimal.Decimal``, nie mit
``float``. Es zaehlen nur ASCII-Ziffern ``0-9``.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, localcontext

_MUSTER = re.compile(
    r"""
    ^
    (?:CHF[ \t]*)?
    (?P<vorzeichen>-)?
    [ \t]*
    (?P<zahl>[0-9]{1,3}(?:['’][0-9]{3})*|[0-9]+)
    (?:\.(?P<nachkomma>[0-9]{1,2}))?
    (?:[ \t]*CHF)?
    $
    """,
    re.IGNORECASE | re.VERBOSE | re.ASCII,
)

_RAPPEN = Decimal("0.05")
_ZWEI_STELLEN = Decimal("0.01")


def _zerlege(wert: str) -> re.Match[str]:
    """Zerlegt einen Betrag und liefert den Treffer des Musters.

    Loest ``ValueError`` aus, wenn die Eingabe kein gueltiger CHF-Betrag ist.
    """
    if not isinstance(wert, str):
        raise ValueError(f"Ungueltiger Betrag: {wert!r}")
    treffer = _MUSTER.match(wert.strip())
    if treffer is None:
        raise ValueError(f"Ungueltiger Betrag: {wert!r}")
    return treffer


def ist_gueltiger_betrag(wert: str) -> bool:
    """Prueft, ob ``wert`` ein gueltiger CHF-Betrag ist.

    Gibt bei jeder Eingabe ``bool`` zurueck und wirft nie eine Ausnahme.
    """
    try:
        normalisiere_betrag(wert)
    except (ValueError, TypeError):
        return False
    return True


def normalisiere_betrag(wert: str) -> str:
    """Gibt den Betrag ohne Tausendertrenner mit zwei Nachkommastellen zurueck.

    Beispiele: ``"CHF 1'234.5"`` wird zu ``"1234.50"``, ``"-0"`` wird zu
    ``"0.00"``. Loest bei ungueltiger Eingabe ``ValueError`` aus.
    """
    treffer = _zerlege(wert)
    zahl = treffer.group("zahl").replace("'", "").replace("’", "")
    nachkomma = treffer.group("nachkomma")
    text = f"{zahl}.{nachkomma}" if nachkomma else zahl
    if treffer.group("vorzeichen"):
        text = f"-{text}"
    betrag = Decimal(text)
    if betrag == 0:
        betrag = betrag.copy_abs()
    return f"{betrag:.2f}"


def runde_auf_5_rappen(betrag: Decimal) -> Decimal:
    """Rundet ``betrag`` kaufmaennisch (ROUND_HALF_UP) auf 0.05.

    Beispiele: ``Decimal("1.025")`` wird zu ``Decimal("1.05")``,
    ``Decimal("1.02")`` zu ``Decimal("1.00")``.
    """
    with localcontext() as kontext:
        kontext.prec = max(28, len(betrag.as_tuple().digits) + 2)
        schritte = (betrag / _RAPPEN).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return (schritte * _RAPPEN).quantize(_ZWEI_STELLEN)

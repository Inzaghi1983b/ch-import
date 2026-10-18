# AGENTS.md - Regeln fuer jeden Coding-Agenten in diesem Repo

Diese Datei gilt unabhaengig vom Agenten (Codex, Claude Code oder andere) und vom Modell.

## Projekt

Kleines Import-Werkzeug fuer Schweizer CSV-Daten: prueft und normalisiert PLZ, AHV-Nummer, Datum,
CHF-Betrag und Telefonnummer und liest CSV-Dateien mit Schweizer Eigenheiten (Semikolon,
Windows-1252). Am Ende gibt es eine Kommandozeile `python -m chimport`.

- Code: `src/chimport/`, ein Modul pro Thema (siehe Modulvertrag)
- Tests: `tests/` (pytest), eine Testdatei pro Modul (z. B. `tests/test_plz.py`)
- Python 3.12, nur Standardbibliothek, keine Laufzeit-Abhaengigkeiten
- Datenklasse: oeffentlich-tauglich. Nur erfundene oder selbst berechnete Testwerte verwenden,
  keine echten Personendaten.

## Fachregeln

- Eingaben sind `str`. Fuehrende und nachfolgende Leerzeichen werden ignoriert.
- Pruef-Funktionen (`ist_gueltige_...`) geben `bool` zurueck und werfen bei ungueltiger Eingabe
  (auch bei Nicht-ASCII-Ziffern wie `٣`) keine Ausnahme.
- Normalisier-Funktionen (`normalisiere_...`) geben die Standardschreibweise als `str` zurueck und
  loesen bei ungueltiger Eingabe `ValueError` aus. `ist_gueltige_x(w)` ist genau dann wahr, wenn
  `normalisiere_x(w)` nicht fehlschlaegt.
- Nur ASCII-Ziffern `0-9` zaehlen als Ziffern (kein `str.isdigit()`, kein `\d` ohne `re.ASCII`).
- Die Regel mit Quelle steht im Docstring des Moduls.
- `src/chimport/__init__.py` nicht aendern; Aufrufer importieren direkt aus dem Modul
  (`from chimport.plz import ...`). So bleiben parallele Aufgaben in getrennten Dateien.
- Jede oeffentliche Funktion hat Typangaben und einen Docstring.

## Modulvertrag (Schnittstellen, nicht abweichen)

| Modul | Funktionen | Standardschreibweise |
|---|---|---|
| `plz.py` | `ist_gueltige_plz`, `normalisiere_plz` | vier Ziffern, `1000` bis `9658` |
| `ahv.py` | `ist_gueltige_ahv`, `normalisiere_ahv` | `756.1234.5678.97` |
| `datum.py` | `ist_gueltiges_datum`, `normalisiere_datum` | ISO `2024-02-29` |
| `betrag.py` | `ist_gueltiger_betrag`, `normalisiere_betrag`, `runde_auf_5_rappen` | `1234.50` |
| `telefon.py` | `ist_gueltige_telefonnummer`, `normalisiere_telefonnummer` | `+41 79 123 45 67` |
| `csvlesen.py` | `lese_csv(pfad) -> list[dict[str, str]]` | - |
| `pruefung.py` | `pruefe_zeilen`, `normalisiere_zeilen`, `Fehler` | - |
| `cli.py`, `__main__.py` | `main(argv) -> int` | - |

## Arbeitsablauf

1. Aufgabe aus dem Issue lesen. Unklarheit nicht raten: Annahme im Pull-Request-Text nennen.
   Weicht deine Umsetzung von einer Acceptance Criterion des Issues ab (oder laesst du eine aus,
   oder gewinnt eine Regel aus dieser Datei gegen das Issue), schreibe im Pull-Request-Text eine
   eigene Zeile `ABWEICHUNG: <was und warum>`. Ein solcher Pull Request wird nicht automatisch
   gemergt, sondern von einem Menschen geprueft.
2. Nur `src/` und `tests/` aendern. README nur, wenn die Aufgabe es verlangt.
3. Fuer jede neue Funktion Tests schreiben, inklusive Grenzfaelle aus dem Issue.
4. Vor dem Abschluss alle drei Pruefungen ausfuehren und gruen machen:
   - `ruff check .`
   - `ruff format --check .` (bei Bedarf vorher `ruff format .`)
   - `pytest`
5. Bleibt eine Pruefung nach drei Korrekturrunden rot: aufhoeren und den Fehler im
   Pull-Request-Text offen beschreiben, nicht Tests abschwaechen oder loeschen.

## Akzeptanztests und Widersprueche

- Akzeptanztests in `tests/akzeptanz/` definieren das fachliche Soll. Widerspricht einer davon einer
  Regel in dieser Datei oder dem Issue, **klaert ein Mensch den Widerspruch vor dem Bau** (Spec oder
  diese Datei per Pull Request anpassen). Das Label `agent` kommt erst danach.
- Stoesst der Agent trotzdem auf einen Widerspruch, baut er nach dem Akzeptanztest und meldet den
  Widerspruch im Pull-Request-Text mit `ABWEICHUNG: <was und warum>`. Diese Meldung wird nie
  weggelassen oder abgeschwaecht; der Pull Request braucht dann einen Menschen.

## Verboten

- Aenderungen an `.github/`, `AGENTS.md`, `pyproject.toml` oder `requirements-dev.txt`.
- Aenderungen an `tests/akzeptanz/`: diese Akzeptanztests gibt ein Mensch vorab vor. Die
  Implementierung muss sie erfuellen; schlagen sie fehl, die Implementierung anpassen oder nach
  drei Runden offen melden.
- Tests loeschen, ueberspringen oder Erwartungen aufweichen, damit sie gruen werden.
- Neue Abhaengigkeiten, Netzwerkzugriffe, Secrets oder Zugangsdaten im Code.
- Personen- oder Kundendaten, ausser die Datenklasse oben erlaubt sie ausdruecklich.

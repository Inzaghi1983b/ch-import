# ch-import

Import-Werkzeug fuer Schweizer CSV-Daten (PLZ, AHV-Nummer, Datum, CHF-Betrag, Telefon). Coding-Agenten setzen Issues autonom um; ein Mensch prueft und merged.
Konventionen: `ai-projects/KONVENTIONEN.md`.

## Ablauf

1. Issue schreiben und Label `agent` setzen.
2. GitHub Agentic Workflows startet den Coding-Agenten (Anbieter: `.github/workflows/shared/anbieter.md`)
   mit Leserechten, Netzwerk-Allowlist und API-Key nur im Proxy.
3. Der Agent setzt das Issue um und fuehrt `ruff` und `pytest` aus (Regeln in `AGENTS.md`).
4. Ein Pruefjob kontrolliert das Ergebnis, danach entsteht ein Draft-Pull-Request.
5. CI (`.github/workflows/ci.yml`) wartet auf den Freigabeklick ("Approve and run") und liefert
   den Pflicht-Check `test`.
6. Ein Mensch prueft, setzt "Ready for review" und merged. Kein automatischer Merge.

## Kostenbremsen

Agent hoechstens 50 AI-Credits (rund 0.50 USD) pro Lauf, Pruefjob 20, alle Laeufe zusammen 200 pro
24 Stunden, hoechstens 30 Minuten. Harte Grenze: Prepaid-Guthaben beim Anbieter.

## Entwicklung lokal

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\ruff check .
.venv\Scripts\pytest
```

## Nutzung

Kommandozeile (nur Standardbibliothek, Python 3.12). Aus dem Repo-Ordner:

```
set PYTHONPATH=src
python -m chimport pruefe kunden.csv --schema "plz=plz,betrag=betrag,tel=telefon,geburt=datum"
python -m chimport normalisiere kunden.csv --schema "plz=plz,betrag=betrag" --ausgabe sauber.csv
```

- **Schema:** `Spalte=typ`, durch Komma getrennt. Typen: `plz`, `ahv`, `datum`, `betrag`, `telefon`,
  `text`. Leere Werte sind immer erlaubt.
- **Einlesen:** UTF-8 (mit/ohne BOM) oder Windows-1252; Trennzeichen `;`, `,` oder Tab wird an der
  Kopfzeile erkannt.
- **Normalisierung:** PLZ `8001`, AHV `756.1234.5678.97`, Datum ISO `2024-02-29`, Betrag `1234.50`
  (Decimal, Tausenderapostroph und `CHF` erlaubt), Telefon `+41 79 123 45 67`. Ausgabe UTF-8 mit
  `;`. Bei Pruefungsfehlern wird nichts geschrieben.
- **Exit-Codes:** 0 ohne Fehler, 1 bei Pruefungsfehlern (eine Zeile je Fehler:
  `Zeile 3, Spalte plz: "99999" ist keine gueltige plz`), 2 bei Aufruf-, Schema- oder Dateifehlern.
- **Als Bibliothek:** `from chimport.plz import ...` (je Modul `ist_gueltige_x` und
  `normalisiere_x`), `chimport.csvlesen.lese_csv` / `lese_csv_mit_kopf`, `chimport.pruefung`.

## Testnachweis

- 345 Tests (`pytest`), `ruff check` und `ruff format --check` gruen, CI auf `main` gruen.
- Unabhaengig vom Agenten geprueft: Faelle aus den Issues, 200 000 Zufalls-AHV-Nummern gegen eine
  eigene EAN-13-Pruefung, 200 000 Zufallsdaten gegen `datetime`, alle PLZ 0000-9999, und ein
  Durchlauf der echten Kommandozeile mit einer Windows-1252-Datei (Umlaut), allen Exit-Codes und
  der Zusicherung, dass bei Fehlern keine Ausgabedatei entsteht. Keine Abweichung.

## Autonomietest 2026-10-16/17 (belegt)

Acht Issues (#1-#8), umgesetzt von Codex mit DeepSeek Flash. Messwerte aus `gh aw audit`
(`agent_usage.json`, `detection_usage.json`), Laufdauer aus `gh run list`.

| Issue | Datei | Lauf | Dauer | Agent: Eingabe (Cache) / Ausgabe | Pruefjob: Eingabe (Cache) / Ausgabe | AI-Credits |
|---|---|---|---|---|---|---|
| #1 | plz.py | 38949628319 | 5 min 13 s | 264 264 (258 560) / 4 898 | 70 419 (55 296) / 578 | 0.91 + 0.56 |
| #2 | ahv.py | 38949631207 | 4 min 54 s | 186 013 (181 120) / 4 199 | 134 878 (115 584) / 1 315 | 0.76 + 0.81 |
| #3 | datum.py | 38949634759 | 4 min 04 s | 266 529 (257 536) / 6 591 | 94 531 (78 080) / 756 | 1.22 + 0.63 |
| #4 | betrag.py | 38949639257 | 5 min 32 s | 373 727 (362 752) / 12 449 | 71 842 (56 448) / 784 | 2.04 + 0.59 |
| #5 | telefon.py | 38949642662 | 6 min 23 s | 424 904 (417 152) / 7 157 | 71 109 (56 320) / 743 | 1.34 + 0.57 |
| #6 | csvlesen.py | 38949647768 | 6 min 00 s | 349 802 (343 936) / 10 348 | 121 893 (105 728) / 1 046 | 1.62 + 0.67 |
| #7 | pruefung.py | 39010714820 | 5 min 34 s | 522 627 (488 192) / 14 597 | 162 514 (134 272) / 2 013 | 3.08 + 1.17 |
| #8 | cli.py | 39022016029 | 4 min 54 s | 624 049 (605 696) / 15 281 | 99 301 (80 384) / 978 | 2.75 + 0.73 |
| **Summe** | | 8 Laeufe | | 3 011 915 (2 914 944) / 75 520 | 826 487 (682 112) / 8 213 | **13.72 + 5.73 = 19.45** |

- **Kosten:** Tokens x Preis aus `shared/anbieter.md` (0.30 USD/Mio. Eingabe, 0.006 USD/Mio.
  Cache, 1.20 USD/Mio. Ausgabe) = rund **0.19 USD** fuer alle acht Issues, im Schnitt 0.024 USD.
  Das ist eine Rechnung aus gemessenen Tokens, kein Abgleich mit der DeepSeek-Abrechnung (offen).
- **Parallelitaet:** Welle 1 (#1-#6) startete am 16.10. zwischen 18:44:20 und 18:44:29 UTC, alle
  sechs Agenten liefen gleichzeitig (Maximum 6), die PRs entstanden zwischen 18:48 und 18:50.
  Danach #7 (abhaengig von #1-#5) und #8 (abhaengig von #6, #7) nacheinander, je ein Agent.
- **Dauer:** Agentenzeit auf dem kritischen Pfad 6 min 23 s + 5 min 34 s + 4 min 54 s = 16 min 51 s.
  Gesamtdauer vom ersten Label (16.10. 18:44) bis zum letzten Merge (17.10. 09:53) 15 h 9 min;
  davon Warten auf menschliche Merges rund 14 h.
- **Qualitaet:** 8 von 8 PRs lieferten im ersten Lauf gruene Checks und erfuellten die Kriterien;
  keine Korrekturrunde, kein weiterer KI-Lauf. Kein Test wurde abgeschwaecht. Im Review fiel eine
  Kopplung auf (`cli.py` importierte private Namen aus `csvlesen.py` und las die Datei doppelt);
  sie wurde von Hand mit `lese_csv_mit_kopf` behoben, ohne KI-Lauf.
- **Menschliche Eingriffe:** Secret setzen (beim ersten Versuch landete es nicht im Repo), acht
  CI-Freigaben ("Approve and run", per API als Admin), drei Merge-Laeufe fuer die acht PRs
  (jeder Merge wurde vom Berechtigungspruefer von Claude Code blockiert und musste vom Menschen
  per Skript ausgefuehrt werden), ein weiterer fuer den Fix. Ohne Merge-Freigabe kein PR
  integriert: Autonomiequote bei Code und Tests 8 von 8, bei Integration 0 von 8.

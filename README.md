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

---
description: Setzt ein Issue mit Label agent um und erstellt einen Draft-Pull-Request
on:
  issues:
    types: [labeled]
    names: [agent]
permissions:
  contents: read
  issues: read
  pull-requests: read
# Anbieter (Agent, Modell, Preis, Anbieter-Host) kommt aus shared/anbieter.md.
# Wechsel: Datei aus ai-projects/anbieter/ dorthin kopieren, Secret setzen, gh aw compile.
imports:
  - shared/anbieter.md
timeout-minutes: 30
max-ai-credits: 50
max-daily-ai-credits: 200
network:
  allowed:
    - defaults
    - python
steps:
  - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
    with:
      python-version: "3.12"
  - run: pip install -r requirements-dev.txt
tools:
  github:
    toolsets: [issues]
  edit:
  bash: ["*"]
safe-outputs:
  create-pull-request:
    draft: true
    title-prefix: "[agent] "
    labels: [agent-pr]
  add-comment:
    max: 1
  threat-detection:
    continue-on-error: false
    max-ai-credits: 20
---

# Issue umsetzen

Du bist der Coding-Agent fuer das Repository `${{ github.repository }}`. Setze Issue
#${{ github.event.issue.number }} um.

Aufgabe aus dem Issue:

${{ steps.sanitized.outputs.text }}

## Vorgehen

1. Lies zuerst `AGENTS.md` und halte dich an alle Regeln dort. Sie gehen dieser Anweisung vor,
   wenn etwas widerspricht.
2. Setze die Aufgabe mit der kleinsten sinnvollen Aenderung in `src/` und `tests/` um.
3. Fuehre `ruff check .`, `ruff format --check .` und `pytest` aus. Behebe Fehler und wiederhole,
   hoechstens drei Korrekturrunden.
4. Erstelle danach genau einen Draft-Pull-Request mit `create_pull_request`:
   - Titel: kurze Beschreibung der Aenderung.
   - Text auf Deutsch: Bezug `Closes #${{ github.event.issue.number }}`, was geaendert wurde,
     Ergebnis der drei Pruefungen (gruen oder rot mit Fehlertext), getroffene Annahmen.
5. Wenn die Aufgabe unklar oder nicht umsetzbar ist: keinen Pull Request, sondern mit
   `add_comment` im Issue kurz erklaeren, was fehlt.

Aendere nie `.github/`, `AGENTS.md`, `pyproject.toml` oder `requirements-dev.txt`, und schwaeche
keine Tests ab.

#!/usr/bin/env bash
# Audit-Script: führt alle Analysetools aus und erzeugt audit-notes.md.
# set -euo pipefail gilt nur für Infrastruktur-Befehle (mkdir, tee).
# Analyse-Tools dürfen bei Befunden exit 1 zurückgeben, ohne das Script zu stoppen.
set -uo pipefail

SRC_DIR="src/arbeitszeit"
REPORT_DIR="docs/audits/reports"

mkdir -p "$REPORT_DIR"

echo "== Ruff (Linting) =="
ruff check src/ tests/ | tee "$REPORT_DIR/ruff-report.txt" || true

echo
echo "== MyPy (Typprüfung) =="
mypy src/arbeitszeit/ | tee "$REPORT_DIR/mypy-report.txt" || true

echo
echo "== Radon (Komplexität) – zyklomatische Komplexität =="
radon cc -s -a "$SRC_DIR" | tee "$REPORT_DIR/radon-cc.txt"

echo
echo "== Radon (Rohdaten) – LOC, Kommentare etc. =="
radon raw "$SRC_DIR" | tee "$REPORT_DIR/radon-raw.txt"

echo
echo "== import-linter (Architektur) =="
lint-imports | tee "$REPORT_DIR/import-linter.txt" || true

echo
echo "== Bandit (Security) =="
bandit -r "$SRC_DIR" -f json -o "$REPORT_DIR/bandit-report.json" || true
echo "JSON-Report: $REPORT_DIR/bandit-report.json"

echo
echo "== pytest + Coverage =="
pytest \
    --cov=arbeitszeit \
    --cov-report=term-missing \
    --cov-report=xml:"$REPORT_DIR/coverage.xml" \
    --cov-report=html:"$REPORT_DIR/htmlcov" \
    | tee "$REPORT_DIR/pytest.txt" || true

echo
echo "== Audit-Notizen generieren =="
python scripts/generate_audit_notes.py --report-dir "$REPORT_DIR"

echo
echo "Audit abgeschlossen. Reports liegen unter: $REPORT_DIR"

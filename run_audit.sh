#!/usr/bin/env bash
# Audit-Script: führt alle Analysetools aus und erzeugt audit-notes.md.
# set -euo pipefail gilt nur für Infrastruktur-Befehle (mkdir, tee).
# Analyse-Tools dürfen bei Befunden exit 1 zurückgeben, ohne das Script zu stoppen.
set -uo pipefail

SRC_DIR="src/arbeitszeit"
DATE=$(date +%Y-%m-%d_%H-%M)
BASE_DIR="docs/audits/reports"
RUN_DIR="$BASE_DIR/$DATE"

mkdir -p "$RUN_DIR"

echo "== Ruff (Linting) =="
ruff check src/ tests/ | tee "$RUN_DIR/ruff-report.txt" || true

echo
echo "== MyPy (Typprüfung) =="
mypy src/arbeitszeit/ | tee "$RUN_DIR/mypy-report.txt" || true

echo
echo "== Radon (Komplexität) – zyklomatische Komplexität =="
radon cc -s -a "$SRC_DIR" | tee "$RUN_DIR/radon-cc.txt"

echo
echo "== Radon (Rohdaten) – LOC, Kommentare etc. =="
radon raw "$SRC_DIR" | tee "$RUN_DIR/radon-raw.txt"

echo
echo "== import-linter (Architektur) =="
lint-imports | tee "$RUN_DIR/import-linter.txt" || true

echo
echo "== Bandit (Security) =="
bandit -r "$SRC_DIR" -f json -o "$RUN_DIR/bandit-report.json" || true
echo "JSON-Report: $RUN_DIR/bandit-report.json"

echo
echo "== pytest + Coverage =="
pytest \
    --cov=arbeitszeit \
    --cov-report=term-missing \
    --cov-report=xml:"$RUN_DIR/coverage.xml" \
    --cov-report=html:"$RUN_DIR/htmlcov" \
    | tee "$RUN_DIR/pytest.txt" || true

echo
echo "== Audit-Notizen generieren =="
python scripts/generate_audit_notes.py \
    --report-dir "$RUN_DIR" \
    --output "$BASE_DIR/audit-notes-$DATE.md"

echo
echo "Reports:     $RUN_DIR"
echo "Audit-Notes: $BASE_DIR/audit-notes-$DATE.md"

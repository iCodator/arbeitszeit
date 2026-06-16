#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="docs/audits/reports"
mkdir -p "$REPORT_DIR"

mapfile -t SOURCE_DIRS < <(
  find . -maxdepth 1 -mindepth 1 -type d \
    ! -name ".git" \
    ! -name ".venv" \
    ! -name "tests" \
    ! -name "docs" \
    ! -name "__pycache__" \
    -exec sh -c 'find "$1" -type f -name "*.py" | grep -q . && printf "%s\n" "${1#./}"' _ {} \; \
  | sort
)

if [ "${#SOURCE_DIRS[@]}" -eq 0 ]; then
  echo "Keine Python-Quellordner im Repo-Root gefunden."
  echo "Bitte prüfe die Projektstruktur."
  exit 1
fi

echo "== Erkannte Quellordner =="
printf ' - %s\n' "${SOURCE_DIRS[@]}" | tee "$REPORT_DIR/source-dirs.txt"

echo
echo "== Ruff (Linting) =="
ruff check "${SOURCE_DIRS[@]}" | tee "$REPORT_DIR/ruff.txt"

echo
echo "== MyPy (Typprüfung) =="
mypy "${SOURCE_DIRS[@]}" | tee "$REPORT_DIR/mypy.txt"

echo
echo "== Radon (Komplexität) – zyklomatische Komplexität =="
radon cc -s -a "${SOURCE_DIRS[@]}" | tee "$REPORT_DIR/radon-cc.txt"

echo
echo "== Radon (Rohdaten) – LOC, Kommentare etc. =="
radon raw "${SOURCE_DIRS[@]}" | tee "$REPORT_DIR/radon-raw.txt"

echo
echo "== import-linter (Architektur) =="
if [ -f importlinter.ini ]; then
  lint-imports | tee "$REPORT_DIR/import-linter.txt"
else
  echo "(importlinter.ini nicht gefunden, Schritt übersprungen)" | tee "$REPORT_DIR/import-linter.txt"
fi

echo
echo "== Bandit (Security) =="
bandit -r "${SOURCE_DIRS[0]}" -f json -o "$REPORT_DIR/bandit-report.json"
if [ "${#SOURCE_DIRS[@]}" -gt 1 ]; then
  for dir in "${SOURCE_DIRS[@]:1}"; do
    bandit -r "$dir" -f json -o "$REPORT_DIR/bandit-$(echo "$dir" | tr '/' '_').json"
  done
fi
echo "Bandit-Reports liegen unter: $REPORT_DIR"

echo
echo "== pytest + Coverage =="
COV_ARGS=()
for dir in "${SOURCE_DIRS[@]}"; do
  COV_ARGS+=( "--cov=$dir" )
done

pytest "${COV_ARGS[@]}" \
  --cov-report=term-missing \
  --cov-report=xml:"$REPORT_DIR/coverage.xml" \
  --cov-report=html:"$REPORT_DIR/htmlcov" \
  | tee "$REPORT_DIR/pytest.txt"

echo
echo "Audit abgeschlossen. Reports liegen unter: $REPORT_DIR"
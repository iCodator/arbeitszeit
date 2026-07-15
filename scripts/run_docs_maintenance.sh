#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${1:-$PWD}"
DOCS_DIR="$REPO_DIR/docs"
CURRENT_DOCS_DIRS=(
  "$DOCS_DIR/02_anwender"
  "$DOCS_DIR/03_installation_technik"
  "$DOCS_DIR/04_betrieb"
  "$DOCS_DIR/05_datenschutz_recht"
  "$DOCS_DIR/06_architektur"
  "$DOCS_DIR/07_pruefberichte"
)
MODULE_DIR="$DOCS_DIR/02_anwender/module"
ARCHIVE_DIR="$DOCS_DIR/archive"
README_FILE="$REPO_DIR/README.md"
PYPROJECT_FILE="$REPO_DIR/pyproject.toml"
AUDIT_SCRIPT="$REPO_DIR/run_audit.sh"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

failures=0
warnings=0

ok() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; warnings=$((warnings+1)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; failures=$((failures+1)); }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

relpath() {
  local p="$1"
  python3 - "$REPO_DIR" "$p" <<'PY'
import os, sys
print(os.path.relpath(sys.argv[2], sys.argv[1]))
PY
}

require_dir() {
  local d="$1"
  [[ -d "$d" ]] && ok "Verzeichnis vorhanden: $(relpath "$d")" || fail "Verzeichnis fehlt: $(relpath "$d")"
}

require_file() {
  local f="$1"
  [[ -f "$f" ]] && ok "Datei vorhanden: $(relpath "$f")" || fail "Datei fehlt: $(relpath "$f")"
}

check_no_archive_scan() {
  if [[ -d "$ARCHIVE_DIR" ]]; then
    ok "docs/archive vorhanden, wird aber bewusst nicht in die Prüfung aktueller Dokumente einbezogen"
  else
    info "docs/archive nicht vorhanden; kein Ausschluss erforderlich"
  fi
}

check_single_h1() {
  local file="$1"
  local count
  count=$(grep -c '^# ' "$file" || true)
  [[ "$count" -eq 1 ]] && ok "$(relpath "$file"): genau 1 H1" || fail "$(relpath "$file"): erwartet genau 1 H1, gefunden: $count"
}

check_header_field() {
  local file="$1"
  local field="$2"
  grep -Eq "^\*\*${field}:\*\* .+" "$file" && ok "$(relpath "$file"): Feld vorhanden: ${field}" || fail "$(relpath "$file\"): Feld fehlt oder leer: ${field}"
}

check_quelldatei_matches() {
  local file="$1"
  local actual expected
  expected="$(relpath "$file")"
  actual=$(sed -n 's/^\*\*Quelldatei:\*\* `\(.*\)`$/\1/p' "$file" | head -n1 || true)
  if [[ -z "$actual" ]]; then
    fail "$(relpath "$file"): Quelldatei nicht auslesbar"
    return
  fi
  [[ "$actual" == "$expected" ]] && ok "$(relpath "$file"): Quelldatei korrekt" || fail "$(relpath "$file"): Quelldatei falsch, ist '$actual', soll '$expected'"
}

check_module_filename_matches_title_soft() {
  local file="$1"
  local base title norm_file norm_title
  base="$(basename "$file" .md)"
  title=$(sed -n 's/^# //p' "$file" | head -n1 || true)
  [[ -z "$title" ]] && return 0
  norm_file=$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')
  norm_title=$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]')
  if [[ "$norm_title" != *"$norm_file"* ]]; then
    warn "$(relpath "$file"): H1 enthält den Dateinamen nicht erkennbar; manuell prüfen"
  else
    ok "$(relpath "$file"): H1 passt erkennbar zum Dateinamen"
  fi
}

check_version_parseable() {
  local file="$1"
  local version
  version=$(sed -n 's/^\*\*Version:\*\* \([0-9][0-9]*\.[0-9][0-9]*\)$/\1/p' "$file" | head -n1 || true)
  [[ -n "$version" ]] && ok "$(relpath "$file"): Version numerisch parsebar" || fail "$(relpath "$file"): Version fehlt oder entspricht nicht dem erwarteten Schema X.Y"
}

check_line_length_soft() {
  local file="$1"
  local hits
  hits=$(awk 'length($0) > 120 {print NR":"length($0)}' "$file" | head -n 5 || true)
  [[ -z "$hits" ]] && ok "$(relpath "$file"): keine auffälligen Zeilen >120 Zeichen" || warn "$(relpath "$file"): auffällige Zeilen >120 Zeichen: $hits"
}

check_bare_urls_soft() {
  local file="$1"
  local hits
  hits=$(grep -nE 'https?://[^)> ]+' "$file" | grep -vE '<https?://' | head -n 5 || true)
  [[ -z "$hits" ]] && ok "$(relpath "$file"): keine offensichtlichen Bare-URLs" || warn "$(relpath "$file"): mögliche Bare-URLs gefunden"
}

check_repo_paths_soft() {
  local file="$1"
  python3 - "$REPO_DIR" "$file" <<'PY'
import re
import sys
from pathlib import Path
repo = Path(sys.argv[1])
file = Path(sys.argv[2])
text = file.read_text(encoding='utf-8')
patterns = re.findall(r'`((?:docs|src|tests|scripts|migrations)/[^`]+|README\.md|pyproject\.toml|run_audit\.sh)`', text)
missing = []
for p in patterns:
    if p.startswith('docs/archive/'):
        continue
    if not (repo / p).exists():
        missing.append(p)
if missing:
    print('\n'.join(missing[:10]))
    sys.exit(2)
PY
  local rc=$?
  [[ $rc -eq 0 ]] && ok "$(relpath "$file"): referenzierte Repo-Pfade vorhanden" || warn "$(relpath "$file"): mindestens ein referenzierter Repo-Pfad fehlt; manuell prüfen"
}

check_run_audit_exists() {
  if [[ -f "$AUDIT_SCRIPT" ]]; then
    ok "run_audit.sh vorhanden"
    [[ -x "$AUDIT_SCRIPT" ]] && ok "run_audit.sh ausführbar" || warn "run_audit.sh ist nicht ausführbar"
  else
    fail "run_audit.sh fehlt"
  fi
}

check_cli_entrypoints_soft() {
  local admin_cli="$REPO_DIR/src/arbeitszeit/presentation/admin_cli/main.py"
  local terminal_ui="$REPO_DIR/src/arbeitszeit/presentation/terminal_ui/main.py"
  [[ -f "$admin_cli" ]] && ok "Admin-CLI-Einstiegspunkt vorhanden" || warn "Admin-CLI-Einstiegspunkt nicht gefunden"
  [[ -f "$terminal_ui" ]] && ok "Terminal-UI-Einstiegspunkt vorhanden" || warn "Terminal-UI-Einstiegspunkt nicht gefunden"
}

check_show_config_related_soft() {
  local show_config="$REPO_DIR/src/arbeitszeit/infrastructure/scripts/show_config.py"
  local config_file="$REPO_DIR/src/arbeitszeit/infrastructure/config_file.py"
  [[ -f "$show_config" ]] && ok "show_config.py vorhanden" || warn "show_config.py nicht gefunden"
  [[ -f "$config_file" ]] && ok "config_file.py vorhanden" || warn "config_file.py nicht gefunden"
}

scan_current_docs_only() {
  local dir
  for dir in "${CURRENT_DOCS_DIRS[@]}"; do
    [[ -d "$dir" ]] || continue
    while IFS= read -r -d '' file; do
      if [[ "$file" == "$ARCHIVE_DIR"/* ]]; then
        continue
      fi
      echo ""
      info "Prüfe $(relpath "$file")"
      check_single_h1 "$file"
      check_header_field "$file" "Kapitel"
      check_header_field "$file" "Version"
      check_header_field "$file" "Stand"
      check_header_field "$file" "Quelldatei"
      check_quelldatei_matches "$file"
      check_version_parseable "$file"
      check_line_length_soft "$file"
      check_bare_urls_soft "$file"
      check_repo_paths_soft "$file"
      if [[ "$file" == "$MODULE_DIR"/*.md ]]; then
        check_module_filename_matches_title_soft "$file"
      fi
    done < <(find "$dir" -type f -name '*.md' -not -path "$ARCHIVE_DIR/*" -print0 | sort -z)
  done
}

info "Starte projektspezifische Dokumentationspflege für arbeitszeit"
require_dir "$DOCS_DIR"
for d in "${CURRENT_DOCS_DIRS[@]}"; do
  require_dir "$d"
done
require_dir "$MODULE_DIR"
require_file "$README_FILE"
require_file "$PYPROJECT_FILE"
check_no_archive_scan
check_run_audit_exists
check_cli_entrypoints_soft
check_show_config_related_soft
scan_current_docs_only

echo ""
info "Zusammenfassung"
echo "Fehler: $failures"
echo "Warnungen: $warnings"

if [[ $failures -gt 0 ]]; then
  fail "Dokumentationspflege fehlgeschlagen"
  exit 1
fi

ok "Dokumentationspflege erfolgreich abgeschlossen"
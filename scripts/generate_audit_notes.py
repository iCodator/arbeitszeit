#!/usr/bin/env python3
"""Wandelt Audit-Report-Dateien in docs/audits/reports/audit-notes.md um.

Liest die Ausgaben von run_audit.sh und erzeugt eine versionierte Markdown-
Datei mit strukturierten Kennzahlen und einem dynamischen Maßnahmenplan.

Verwendung:
    python scripts/generate_audit_notes.py
    python scripts/generate_audit_notes.py --report-dir docs/audits/reports
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Typen
# ---------------------------------------------------------------------------

ReportData = dict[str, Any]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def parse_ruff(path: Path) -> ReportData:
    """Parst ruff-report.txt.

    Rückgabe:
        total       – Gesamtanzahl Fehler
        by_code     – Counter {code: count}
        e501        – Anzahl E501 (line-too-long)
        f401        – Anzahl F401 (unused-import)
        bugbear     – Anzahl B*-Fehler
        available   – True wenn Datei vorhanden
    """
    if not path.exists():
        return {"available": False}

    text = path.read_text(encoding="utf-8")
    codes: list[str] = re.findall(r"^([A-Z]\d+)\s", text, re.MULTILINE)
    by_code: Counter[str] = Counter(codes)

    return {
        "available": True,
        "total": len(codes),
        "by_code": dict(by_code.most_common()),
        "e501": by_code.get("E501", 0),
        "f401": by_code.get("F401", 0),
        "bugbear": sum(v for k, v in by_code.items() if k.startswith("B")),
    }


def parse_mypy(path: Path) -> ReportData:
    """Parst mypy-report.txt.

    Rückgabe:
        available, success, total_errors, source_files, errors (list[str])
    """
    if not path.exists():
        return {"available": False}

    text = path.read_text(encoding="utf-8")

    m = re.search(r"^Success:\s+no issues found in (\d+) source files", text, re.MULTILINE)
    if m:
        return {
            "available": True,
            "success": True,
            "total_errors": 0,
            "source_files": int(m.group(1)),
            "errors": [],
        }

    error_lines = [ln for ln in text.splitlines() if " error:" in ln]
    return {
        "available": True,
        "success": False,
        "total_errors": len(error_lines),
        "source_files": None,
        "errors": error_lines[:10],
    }


def parse_radon_cc(path: Path) -> ReportData:
    """Parst radon-cc.txt (zyklomatische Komplexität).

    Rückgabe:
        available, avg_grade, avg_cc, blocks, hotspots (list[dict])
    """
    if not path.exists():
        return {"available": False}

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Durchschnittskomplexität aus letzter Zeile
    avg_grade = "?"
    avg_cc = 0.0
    blocks = 0
    for ln in reversed(lines):
        m = re.search(r"Average complexity:\s+([A-F])\s+\((\d+\.?\d*)\)", ln)
        if m:
            avg_grade = m.group(1)
            avg_cc = float(m.group(2))
        m2 = re.search(r"(\d+) blocks", ln)
        if m2:
            blocks = int(m2.group(1))
        if avg_grade != "?" and blocks:
            break

    # Hotspots: CC >= 10
    hotspots: list[dict[str, Any]] = []
    current_file = ""
    block_re = re.compile(r"^\s+[FMC]\s+\d+:\d+\s+(.+?)\s+-\s+[A-F]\s+\((\d+)\)")
    file_re = re.compile(r"^src/")

    for ln in lines:
        if file_re.match(ln):
            current_file = ln.strip().removeprefix("src/arbeitszeit/")
        m = block_re.match(ln)
        if m:
            cc_val = int(m.group(2))
            if cc_val >= 10:
                hotspots.append(
                    {
                        "file": current_file,
                        "block": m.group(1),
                        "cc": cc_val,
                    }
                )

    hotspots.sort(key=lambda x: x["cc"], reverse=True)

    return {
        "available": True,
        "avg_grade": avg_grade,
        "avg_cc": avg_cc,
        "blocks": blocks,
        "hotspots": hotspots,
    }


def parse_radon_raw(path: Path) -> ReportData:
    """Parst radon-raw.txt (LOC-Metriken).

    Rückgabe:
        available, total_sloc, total_loc
    """
    if not path.exists():
        return {"available": False}

    text = path.read_text(encoding="utf-8")
    sloc_vals = [int(m) for m in re.findall(r"^\s+SLOC:\s+(\d+)", text, re.MULTILINE)]
    loc_vals = [int(m) for m in re.findall(r"^\s+LOC:\s+(\d+)", text, re.MULTILINE)]

    return {
        "available": True,
        "total_sloc": sum(sloc_vals),
        "total_loc": sum(loc_vals),
    }


def parse_import_linter(path: Path) -> ReportData:
    """Parst import-linter.txt.

    Rückgabe:
        available, kept, broken, violations (list[str])
    """
    if not path.exists():
        return {"available": False}

    text = path.read_text(encoding="utf-8")
    m = re.search(r"Contracts:\s+(\d+)\s+kept,\s+(\d+)\s+broken", text)
    if not m:
        return {"available": True, "kept": 0, "broken": 0, "violations": []}

    kept = int(m.group(1))
    broken = int(m.group(2))

    violations: list[str] = []
    if broken > 0:
        for ln in text.splitlines():
            if "->" in ln and "BROKEN" not in ln and "Contracts" not in ln:
                violations.append(ln.strip())

    return {
        "available": True,
        "kept": kept,
        "broken": broken,
        "violations": violations,
    }


def parse_bandit(path: Path) -> ReportData:
    """Parst bandit-report.json.

    Rückgabe:
        available, high, medium, low, loc, nosec, critical (list[dict])
    """
    if not path.exists():
        return {"available": False}

    data = json.loads(path.read_text(encoding="utf-8"))
    totals = data.get("metrics", {}).get("_totals", {})

    critical = [
        {
            "id": r["test_id"],
            "name": r["test_name"],
            "severity": r["issue_severity"],
            "file": r["filename"].removeprefix("src/arbeitszeit/"),
            "line": r["line_number"],
            "text": r["issue_text"],
        }
        for r in data.get("results", [])
        if r["issue_severity"] in ("HIGH", "MEDIUM")
    ]

    return {
        "available": True,
        "high": int(totals.get("SEVERITY.HIGH", 0)),
        "medium": int(totals.get("SEVERITY.MEDIUM", 0)),
        "low": int(totals.get("SEVERITY.LOW", 0)),
        "loc": int(totals.get("loc", 0)),
        "nosec": int(totals.get("nosec", 0)),
        "critical": critical,
    }


def parse_coverage(path: Path, low_threshold: float = 0.60) -> ReportData:
    """Parst coverage.xml (Cobertura-Format).

    Rückgabe:
        available, line_rate, lines_valid, lines_covered, low_coverage (list[dict])
    """
    if not path.exists():
        return {"available": False}

    tree = ET.parse(path)
    root = tree.getroot()

    line_rate = float(root.attrib.get("line-rate", 0))
    lines_valid = int(root.attrib.get("lines-valid", 0))
    lines_covered = int(root.attrib.get("lines-covered", 0))

    low_coverage: list[dict[str, Any]] = []
    for cls in root.iter("class"):
        rate = float(cls.attrib.get("line-rate", 1))
        if rate < low_threshold:
            fname = cls.attrib.get("filename", "")
            fname = fname.removeprefix("src/arbeitszeit/")
            low_coverage.append({"file": fname, "rate": rate})

    low_coverage.sort(key=lambda x: x["rate"])

    return {
        "available": True,
        "line_rate": line_rate,
        "lines_valid": lines_valid,
        "lines_covered": lines_covered,
        "low_coverage": low_coverage,
    }


def count_tests(project_root: Path) -> ReportData:
    """Zählt Testdateien nach Kategorie."""
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return {"available": False}

    def _count(subdir: str) -> int:
        d = tests_dir / subdir
        if not d.exists():
            return 0
        return len(
            [
                f
                for f in d.glob("test_*.py")
                if f.name not in ("conftest.py", "__init__.py")
            ]
        )

    return {
        "available": True,
        "domain": _count("domain"),
        "application": _count("application"),
        "integration": _count("integration"),
        "e2e": _count("e2e"),
    }


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


def _na(available: object) -> str:
    return "" if available else " _(Report nicht verfügbar)_"


def render(data: dict[str, ReportData], timestamp: datetime) -> str:
    ruff = data["ruff"]
    mypy = data["mypy"]
    radon_cc = data["radon_cc"]
    radon_raw = data["radon_raw"]
    imp = data["import_linter"]
    bandit = data["bandit"]
    cov = data["coverage"]
    tests = data["tests"]

    ts_display = timestamp.strftime("%Y-%m-%d %H:%M")  # lokale Zeit
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # Meta: UTC

    lines: list[str] = []
    a = lines.append

    # ── Titel + Meta ────────────────────────────────────────────────────────
    a(f"# Code-Audit arbeitszeit – Stand {ts_display}")
    a("")
    a(f"<!-- meta: generated_at={ts_iso} -->")
    a("")

    # ── Überblick ────────────────────────────────────────────────────────────
    a("## Überblick")
    a("")
    if radon_raw.get("available"):
        sloc = int(radon_raw["total_sloc"])
        a(f"- Codebasis: ca. {sloc / 1000:.1f} KLoC (SLOC) im Paket `arbeitszeit`")
    else:
        a("- Codebasis: _(nicht verfügbar)_")

    if tests.get("available"):
        d = tests["domain"]
        ap = tests["application"]
        it = tests["integration"]
        e2e = tests["e2e"]
        a(f"- Tests: {d} unit (domain) | {ap} application | {it} integration | {e2e} e2e")
    else:
        a("- Tests: _(nicht ermittelbar)_")
    a("")

    # ── Linting ──────────────────────────────────────────────────────────────
    a("## Linting (Ruff)")
    a("")
    if ruff.get("available"):
        total = ruff["total"]
        a(f"- Gesamtanzahl Probleme: **{total}**")
        a("- Hauptkategorien:")
        a(f"  - E501 (line-too-long): {ruff['e501']}")
        a(f"  - F401 (unused-import): {ruff['f401']}")
        a(f"  - B-Serie (bugbear): {ruff['bugbear']}")
        by_code = dict(ruff["by_code"])
        others = {
            k: v
            for k, v in by_code.items()
            if k not in ("E501", "F401") and not k.startswith("B")
        }
        for code, cnt in sorted(others.items()):
            a(f"  - {code}: {cnt}")
    else:
        a("- _(Report nicht verfügbar)_")
    a("")

    # ── Typprüfung ───────────────────────────────────────────────────────────
    a("## Typprüfung (Mypy)")
    a("")
    if mypy.get("available"):
        if mypy.get("success"):
            a("- Fehler insgesamt: **0**")
            a(f"- {mypy['source_files']} Quelldateien geprüft, keine Typfehler")
            a("- Typische Muster: –")
        else:
            total_err = mypy["total_errors"]
            a(f"- Fehler insgesamt: **{total_err}**")
            errors: list[str] = mypy["errors"]
            if errors:
                a("- Typische Muster:")
                for e in errors[:5]:
                    a(f"  - `{e.strip()}`")
    else:
        a("- _(Report nicht verfügbar)_")
    a("")

    # ── Komplexität ──────────────────────────────────────────────────────────
    a("## Komplexität (Radon)")
    a("")
    if radon_cc.get("available"):
        a(
            f"- Durchschnittliche CC: **{radon_cc['avg_grade']} ({radon_cc['avg_cc']:.2f})**,"
            f" {radon_cc['blocks']} Blöcke analysiert"
        )
        hotspots: list[dict[str, Any]] = radon_cc["hotspots"]
        if hotspots:
            a("- Hotspots (CC ≥ 10):")
            a("")
            a("  | Datei | Block | CC |")
            a("  |-------|-------|:--:|")
            for h in hotspots:
                a(f"  | `{h['file']}` | `{h['block']}` | {h['cc']} |")
        else:
            a("- Hotspots (CC ≥ 10): –")
    else:
        a("- _(Report nicht verfügbar)_")
    a("")

    # ── Architektur ──────────────────────────────────────────────────────────
    a("## Architektur (import-linter)")
    a("")
    if imp.get("available"):
        kept = imp["kept"]
        broken = imp["broken"]
        a(f"- Contracts geprüft: {kept}")
        a(f"- Verstöße: **{broken}**")
        violations: list[str] = imp["violations"]
        if violations:
            a("- Verstoßdetails:")
            for v in violations:
                a(f"  - `{v}`")
    else:
        a("- _(Report nicht verfügbar – lint-imports nicht ausgeführt)_")
    a("")

    # ── Security ─────────────────────────────────────────────────────────────
    a("## Security (Bandit)")
    a("")
    if bandit.get("available"):
        a(f"- High: **{bandit['high']}** / Medium: **{bandit['medium']}** / Low: {bandit['low']}")
        a(f"- LOC gescannt: {bandit['loc']}")
        if bandit["nosec"]:
            a(f"- nosec-Marker: {bandit['nosec']}")
        critical: list[dict[str, Any]] = bandit["critical"]
        if critical:
            a("- Kritische Stellen (HIGH + MEDIUM):")
            a("")
            a("  | ID | Datei | Zeile | Beschreibung |")
            a("  |----|-------|:-----:|-------------|")
            for c in critical:
                text = str(c["text"])[:60]
                a(f"  | `{c['id']}` | `{c['file']}` | {c['line']} | {text} |")
        else:
            a("- Kritische Stellen (HIGH + MEDIUM): –")
    else:
        a("- _(Report nicht verfügbar)_")
    a("")

    # ── Tests & Coverage ─────────────────────────────────────────────────────
    a("## Tests & Coverage")
    a("")
    if cov.get("available"):
        pct = float(cov["line_rate"]) * 100
        covered = cov['lines_covered']
        valid = cov['lines_valid']
        a(f"- Gesamt-Coverage: **{pct:.1f} %** ({covered} / {valid} Zeilen)")
        low: list[dict[str, Any]] = cov["low_coverage"]
        if low:
            a("- Dateien mit Coverage < 60 %:")
            a("")
            a("  | Datei | Coverage |")
            a("  |-------|:--------:|")
            for item in low:
                a(f"  | `{item['file']}` | {float(item['rate']) * 100:.0f} % |")
        else:
            a("- Dateien mit Coverage < 60 %: –")
    else:
        a("- _(Report nicht verfügbar)_")
    a("")

    # ── Maßnahmenplan ────────────────────────────────────────────────────────
    a("## Maßnahmenplan")
    a("")
    actions: list[str] = _build_actions(data)
    if actions:
        for i, action in enumerate(actions, 1):
            a(f"{i}. {action}")
    else:
        a("_Keine offenen Maßnahmen identifiziert – alle Checks bestanden._")
    a("")

    return "\n".join(lines)


def _build_actions(data: dict[str, ReportData]) -> list[str]:
    """Erzeugt dynamisch priorisierte Maßnahmen aus den Befunden."""
    actions: list[str] = []

    bandit = data["bandit"]
    if bandit.get("available") and (int(bandit.get("high", 0)) + int(bandit.get("medium", 0))) > 0:
        actions.append(
            f"Security-Funde mit HIGH/MEDIUM-Schwere priorisiert beheben"
            f" ({bandit['high']} HIGH, {bandit['medium']} MEDIUM)."
        )

    imp = data["import_linter"]
    if imp.get("available") and int(imp.get("broken", 0)) > 0:
        actions.append(
            f"Architekturverstöße gegen Layer-Contract eliminieren ({imp['broken']} Verstöße)."
        )

    mypy = data["mypy"]
    if mypy.get("available") and not mypy.get("success") and int(mypy.get("total_errors", 0)) > 0:
        actions.append(
            f"Typfehler beheben ({mypy['total_errors']} Fehler in Mypy-Prüfung)."
        )

    ruff = data["ruff"]
    if ruff.get("available") and int(ruff.get("total", 0)) > 0:
        actions.append(
            f"Linting-Fehler beheben ({ruff['total']} Befunde in Ruff-Prüfung)."
        )

    radon_cc = data["radon_cc"]
    hotspots: list[dict[str, Any]] = radon_cc.get("hotspots", [])
    severe = [h for h in hotspots if int(h["cc"]) >= 15]
    if severe:
        names = ", ".join(f"`{h['block']}`" for h in severe[:3])
        actions.append(
            f"Komplexe Funktionen refaktorieren (CC ≥ 15): {names}."
        )

    cov = data["coverage"]
    if cov.get("available"):
        pct = float(cov["line_rate"]) * 100
        if pct < 80:
            low_count = len(cov.get("low_coverage", []))
            actions.append(
                f"Tests für Module mit Coverage < 60 % ergänzen"
                f" ({low_count} Dateien betroffen, Gesamt-Coverage: {pct:.1f} %)."
            )

    return actions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Erzeugt audit-notes.md aus den Audit-Report-Dateien.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("docs/audits/reports"),
        help="Verzeichnis mit den Report-Dateien (Standard: docs/audits/reports)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Ausgabedatei (Standard: <report-dir>/audit-notes.md)",
    )
    args = parser.parse_args(argv)

    report_dir: Path = args.report_dir
    project_root = Path(__file__).parent.parent

    if not report_dir.exists():
        print(f"Fehler: Report-Verzeichnis nicht gefunden: {report_dir}", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now().astimezone()  # lokale Systemzeit mit Offset
    date_tag = timestamp.strftime("%Y-%m-%d_%H-%M")
    output = args.output or report_dir / f"audit-notes-{date_tag}.md"

    data: dict[str, ReportData] = {
        "ruff": parse_ruff(report_dir / "ruff-report.txt"),
        "mypy": parse_mypy(report_dir / "mypy-report.txt"),
        "radon_cc": parse_radon_cc(report_dir / "radon-cc.txt"),
        "radon_raw": parse_radon_raw(report_dir / "radon-raw.txt"),
        "import_linter": parse_import_linter(report_dir / "import-linter.txt"),
        "bandit": parse_bandit(report_dir / "bandit-report.json"),
        "coverage": parse_coverage(report_dir / "coverage.xml"),
        "tests": count_tests(project_root),
    }

    md = render(data, timestamp)
    output.write_text(md, encoding="utf-8")
    print(f"audit-notes geschrieben: {output}")


if __name__ == "__main__":
    main()

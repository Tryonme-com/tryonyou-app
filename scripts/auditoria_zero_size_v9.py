#!/usr/bin/env python3
"""
Auditoría Zero-Size / V9 Identity para artefactos operativos del monorepo.

Objetivo:
- Detectar rastros de tallas clásicas y medidas corporales en componentes críticos.
- Verificar encadenado Fabric Fit Comparator + sello de patente.
- Generar un reporte JSON reutilizable para ejecución táctica.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "src"
API_DIR = ROOT / "api"
REPORT_PATH = ROOT / "logs" / "zero_size_v9_audit_report.json"

COMPONENT_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".py"}
TARGET_COMPONENT_COUNT = 66
TOKEN_RE = re.compile(r"\b(?:XS|S|M|L|XL|XXL)\b")
MEASURE_RE = re.compile(
    r"\b(?:chest|waist|hip|bust|shoulder_w|hip_y|measurement|measurements|size_confirmed)\b",
    re.IGNORECASE,
)
IGNORE_SNIPPETS = (
    "measurementId",  # Firebase analytics identifier, no biometría corporal.
)


@dataclass
class Match:
    file: str
    line: int
    snippet: str


def _iter_component_files() -> list[Path]:
    files: set[Path] = set()
    for base in (SRC_DIR, API_DIR):
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.suffix.lower() in COMPONENT_EXTENSIONS and path.is_file():
                files.add(path)
    # Añadimos módulos operativos fuera de src/api para blindaje de contrato Make/cart.
    for extra in (
        ROOT / "smart_cart.py",
        ROOT / "core_mirror_orchestrator.py",
        ROOT / "Espejo Digital -> Make.py",
    ):
        if extra.is_file():
            files.add(extra)
    return sorted(files)


def _scan_file(path: Path) -> tuple[list[Match], list[Match]]:
    token_hits: list[Match] = []
    measure_hits: list[Match] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return token_hits, measure_hits

    rel = str(path.relative_to(ROOT))
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if any(ignore in line for ignore in IGNORE_SNIPPETS):
            continue
        if TOKEN_RE.search(line):
            token_hits.append(Match(file=rel, line=idx, snippet=line[:220]))
        if MEASURE_RE.search(line):
            measure_hits.append(Match(file=rel, line=idx, snippet=line[:220]))
    return token_hits, measure_hits


def _fabric_fit_status() -> dict[str, object]:
    comparator_path = SRC_DIR / "lib" / "fabricFitComparator.ts"
    app_path = SRC_DIR / "App.tsx"
    index_path = ROOT / "index.html"
    status = {
        "comparator_file_exists": comparator_path.is_file(),
        "app_uses_fit_event": False,
        "index_dispatches_fit_event": False,
        "patent_reference_found": False,
    }

    if comparator_path.is_file():
        ctext = comparator_path.read_text(encoding="utf-8")
        status["patent_reference_found"] = "PCT/EP2025/067317" in ctext or "Zero-Size" in ctext
    if app_path.is_file():
        atext = app_path.read_text(encoding="utf-8")
        status["app_uses_fit_event"] = "tryonyou:fit" in atext
    if index_path.is_file():
        itext = index_path.read_text(encoding="utf-8")
        status["index_dispatches_fit_event"] = "tryonyou:fit" in itext
    return status


def main() -> int:
    files = _iter_component_files()
    token_hits: list[Match] = []
    measure_hits: list[Match] = []
    for path in files:
        tk, ms = _scan_file(path)
        token_hits.extend(tk)
        measure_hits.extend(ms)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "scope": "src+api+módulos operativos críticos",
        "target_components": TARGET_COMPONENT_COUNT,
        "component_files_audited": len(files),
        "target_reached": len(files) >= TARGET_COMPONENT_COUNT,
        "classical_size_token_hits": [asdict(m) for m in token_hits],
        "measure_term_hits": [asdict(m) for m in measure_hits],
        "fabric_fit_comparator": _fabric_fit_status(),
        "status": "ok",
    }
    REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"component_files_audited={len(files)}")
    print(f"classical_size_token_hits={len(token_hits)}")
    print(f"measure_term_hits={len(measure_hits)}")
    print(f"report={REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

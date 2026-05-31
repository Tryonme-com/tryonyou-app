#!/usr/bin/env python3
"""
Parsea volcados de auditoría (p. ej. salida de docker logs redirigida a un fichero).

Extrae candidatos a IDs de pago (Stripe, request) e importes para cruce con Linear / dashboard.

Uso (cada línea es un comando aparte; evita pipes sin comillas en Zsh):

  python3 scripts/parse_audit_log_v11.py
  python3 scripts/parse_audit_log_v11.py ruta/al/log.txt
  python3 scripts/parse_audit_log_v11.py --archive salida/audit_2026-04-24.jsonl
  python3 scripts/parse_audit_log_v11.py --audit-gate

Puerta FINANCE_BRIDGE (finance_bridge): el fichero debe incluir una señal positiva
de reconciliación, por ejemplo una línea exacta:

  FINANCE_BRIDGE_AUDIT: MATCHED

o JSON con reconciliation_status OK (salida de financial_compliance). Si aparece
OVERALLOCATED_LEDGER o FINANCE_BRIDGE_AUDIT: FAIL, la puerta falla.

No sustituye la verificación en Stripe/Qonto: solo estructura lo leíble del registro.
Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

# Stripe
_RE_PI = re.compile(r"\b(pi_[A-Za-z0-9_]+)")
_RE_CH = re.compile(r"\b(ch_[A-Za-z0-9_]+)")
_RE_PO = re.compile(r"\b(po_[A-Za-z0-9_]+)")
# Request / trazas
_RE_REQ = re.compile(r"(?:req_|request[_\s-]*id[:\s]+|Request-ID[:\s]+)([A-Za-z0-9_-]{8,})")
_RE_UUID = re.compile(
    r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b",
    re.I,
)
# Importes (EUR, €, decimales)
_RE_AMOUNT = re.compile(
    r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|EUR|eur)",
    re.I,
)
_RE_CENTS = re.compile(r"amount[\":\s]+(\d{4,})\b", re.I)
_RE_PENDING = re.compile(r"pending|unreconcil|not\s+reconcil|no\s+match", re.I)

# Puerta para logic/finance_bridge.py: señal explícita o JSON de compliance
_RE_AUDIT_POSITIVE = re.compile(
    r"(?is)(?:^|\n)\s*FINANCE_BRIDGE_AUDIT:\s*MATCHED\s*(?:\n|$)"
    r'|"reconciliation_status"\s*:\s*"OK"'
    r"|reconciliation_status\s*[:=]\s*[\"']?OK[\"']?(?!\w)",
)
_RE_AUDIT_NEGATIVE = re.compile(
    r"(?is)OVERALLOCATED_LEDGER|DISCREPANCY_DETECTED"
    r"|(?:^|\n)\s*FINANCE_BRIDGE_AUDIT:\s*(?:FAIL|BLOCK)\s*(?:\n|$)",
)


def audit_reconciliation_matched(audit_path: Path | str) -> tuple[bool, str]:
    """
    Devuelve (True, razon) solo si ``audit_log_v11.txt`` (o ruta dada) contiene
    señal positiva de reconciliación y no contiene señales negativas conocidas.
    """
    p = Path(audit_path)
    if not p.is_file():
        return False, "missing_file"
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return False, "empty_file"
    if _RE_AUDIT_NEGATIVE.search(text):
        return False, "negative_signal_in_log"
    if _RE_AUDIT_POSITIVE.search(text):
        return True, "matched_marker_found"
    return False, "no_positive_audit_gate_marker"


def parse_lines(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        refs: list[str] = []
        for rx in (_RE_PI, _RE_CH, _RE_PO, _RE_UUID):
            refs.extend(rx.findall(line))
        mreq = _RE_REQ.search(line)
        if mreq:
            refs.append(mreq.group(1).strip())
        # dedup preserve order
        seen: set[str] = set()
        ref_out = []
        for r in refs:
            if r not in seen:
                seen.add(r)
                ref_out.append(r)
        amounts: list[str] = []
        for m in _RE_AMOUNT.finditer(line):
            amounts.append(m.group(1))
        for m in _RE_CENTS.finditer(line):
            amounts.append(f"cents={m.group(1)}")
        row: dict[str, object] = {
            "line": i,
            "raw": line[:2000],
            "reference_candidates": ref_out,
            "amount_snippets": amounts,
            "flag_pendingish": bool(_RE_PENDING.search(line)),
        }
        if ref_out or amounts or row["flag_pendingish"]:
            rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse audit log dump (V11) for cross-check.")
    ap.add_argument(
        "--audit-gate",
        action="store_true",
        help="Solo comprobar puerta MATCHED (JSON en stdout, exit 0 si OK)",
    )
    ap.add_argument(
        "input_path",
        nargs="?",
        default="audit_log_v11.txt",
        help="Fichero de volcado (defecto: audit_log_v11.txt en la raíz)",
    )
    ap.add_argument(
        "--archive",
        metavar="OUT.jsonl",
        help="Escribir resultados estructurados (JSONL) y copiar el origen junto a OUT si existe.",
    )
    args = ap.parse_args()
    p = Path(args.input_path)
    if args.audit_gate:
        matched, reason = audit_reconciliation_matched(p)
        print(
            json.dumps(
                {"matched": matched, "reason": reason, "path": str(p.resolve())},
                ensure_ascii=False,
            ),
            flush=True,
        )
        raise SystemExit(0 if matched else 1)

    if not p.is_file():
        print(f"No existe el fichero: {p}", flush=True)
        raise SystemExit(1)
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print(
            f"Fichero vacío: {p}. Genera el volcado en dos pasos (Zsh seguro, sin history-expand):\n"
            f"  docker logs NOMBRE_CONTENEDOR --since 24h > audit_log_v11.txt\n"
            f"  grep -i transaction audit_log_v11.txt > audit_signals.txt\n"
            "Tras reconciliar, añade una línea al log de auditoría:\n"
            "  FINANCE_BRIDGE_AUDIT: MATCHED\n",
            flush=True,
        )
        raise SystemExit(0)

    rows = parse_lines(text)
    summary = {
        "source": str(p.resolve()),
        "lines_total": len(text.splitlines()),
        "lines_with_signals": len(rows),
        "parsed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2))

    if args.archive:
        out = Path(args.archive)
        out.parent.mkdir(parents=True, exist_ok=True)
        meta = {**summary, "archive": str(out.resolve())}
        with out.open("w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        snap = out.with_name(out.stem + "_source" + p.suffix)
        shutil.copy2(p, snap)
        print(f"Archivado JSONL+origen: {out} y {snap}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Parsea volcados de auditoría (p. ej. salida de docker logs | grep transaction).
Extrae candidatos a IDs de pago (Stripe, request) e importes para cruce con Linear / dashboard.

Uso:
  python3 scripts/parse_audit_log_v11.py
  python3 scripts/parse_audit_log_v11.py ruta/al/log.txt
  python3 scripts/parse_audit_log_v11.py --archive salida/audit_2026-04-24.jsonl

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
    if not p.is_file():
        print(f"No existe el fichero: {p}", flush=True)
        raise SystemExit(1)
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print(
            f"Fichero vacío: {p}. Genera el volcado p. ej.:\n"
            f'  docker logs lafayette-marais-node --since 24h | grep -i "transaction" > audit_log_v11.txt',
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

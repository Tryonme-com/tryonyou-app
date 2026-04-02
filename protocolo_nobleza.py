"""
Protocolo de Nobleza V15 — portal estático `alliance_exclusive.html` + sello en manifiesto.

No sustituye `index.html`. Git: push normal (sin --force salvo TRYONYOU_NOBILITY_FORCE_PUSH=1).

TRYONYOU_SKIP_GIT=1 — solo archivos locales.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLIANCE_HTML = ROOT / "alliance_exclusive.html"
MANIFEST = ROOT / "production_manifest.json"

COMMIT_MSG = (
    "SOVEREIGNTY: Protocolo Nobleza V15 — portal alliance_exclusive (palabra sobre ceros). "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

HTML_BODY = """
<body style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;margin:0;padding:20px;">
    <div style="border:1px solid #D4AF37;padding:60px;max-width:900px;background:rgba(5,5,5,0.98);box-shadow: 0 0 80px rgba(212,175,55,0.15);">
        <h1 style="font-size:3.5rem;letter-spacing:12px;margin-bottom:10px;text-transform:uppercase;">ALLIANCE DE NOBLESSE</h1>
        <h2 style="color:#fff;text-transform:uppercase;letter-spacing:4px;border-bottom:1px solid #D4AF37;padding-bottom:20px;display:inline-block;">RÉSERVÉ AUX CHEVALIERS DU RETAIL</h2>

        <p style="font-size:1.4rem;line-height:2;color:#eee;margin-top:40px;">
            « La classe et le luxe marchent main dans la main. La technologie Zero-Size n'appartient qu'à ceux dont l'esprit est à la hauteur de leur nom. »
        </p>

        <div style="margin-top:50px;padding:30px;border:1px solid #333;background:rgba(255,255,255,0.02);">
            <p style="color:#D4AF37;font-size:1.1rem;margin:0;">TARIF D'HONNEUR (MOT D'ARCHITECTE) :</p>
            <p style="font-size:4rem;font-weight:bold;color:#fff;margin:10px 0;">16.200 € TTC</p>
            <p style="color:#888;font-size:0.9rem;">Exclusivité Code Postal 75009 / 75007 | Google Studio Powered</p>
        </div>

        <p style="font-style:italic;font-size:1.1rem;color:#D4AF37;margin-top:50px;opacity:0.8;">
            « De rien ne sert de porter du blanc si l'esprit n'est pas pur. »
        </p>

        <div style="margin-top:40px;font-size:0.8rem;opacity:0.6;color:#888;text-align:left;border-left:2px solid #D4AF37;padding-left:20px;">
            <strong>RUBÉN ESPINAR RODRÍGUEZ</strong><br>
            Chief Sovereign Architect | Lead Visionary<br>
            Patent PCT/EP2025/067317
        </div>
    </div>
</body>
"""


def _full_html() -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"fr\">\n<head>\n"
        '<meta charset="UTF-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        "<title>Alliance de Noblesse — TryOnYou</title>\n</head>\n"
        f"{HTML_BODY.strip()}\n</html>\n"
    )


def _merge_manifest() -> None:
    if not MANIFEST.is_file():
        return
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["nobility_protocol_v15"] = {
        "status": "ACTIVE",
        "honor_rate_ttc": "16.200 € TTC",
        "zones": ["75009", "75007"],
        "portal_file": "alliance_exclusive.html",
        "activated_at_utc": ts,
        "patent": "PCT/EP2025/067317",
    }
    data.setdefault("strategic_note", "")
    if not isinstance(data.get("strategic_note"), dict):
        data["strategic_note"] = {
            "nobility_v15": "Word over zeros — alliance portal for qualifying retail partners",
            "updated_utc": ts,
        }
    elif isinstance(data["strategic_note"], dict):
        data["strategic_note"]["nobility_v15"] = "Word over zeros — alliance portal"
        data["strategic_note"]["updated_utc"] = ts
    MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def ejecutar_protocolo_nobleza() -> int:
    print("\n--- 🔱 ACTIVANDO PROTOCOLO DE NOBLEZA V15 ---")

    ALLIANCE_HTML.write_text(_full_html(), encoding="utf-8")
    print(f"✅ Portal: {ALLIANCE_HTML.name}")

    _merge_manifest()
    print("✅ production_manifest.json — nobility_protocol_v15 fusionado.")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("TRYONYOU_SKIP_GIT=1 — sin commit/push.")
        return 0

    _git(["add", "."])
    rc = _git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Sin commit (¿árbol limpio?).", file=sys.stderr)
    if os.environ.get("TRYONYOU_NOBILITY_FORCE_PUSH", "").strip() == "1":
        rc = _git(["push", "origin", "main", "--force"])
    else:
        rc = _git(["push", "origin", "main"])
    if rc != 0:
        print("⚠️  git push falló.", file=sys.stderr)
        return rc
    print("\n--- 🔱 Nobleza V15 sellada en main ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(ejecutar_protocolo_nobleza())

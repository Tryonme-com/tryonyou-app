"""
Sellado final « Architecte souverain » — pantalla DÉSACTIVÉ para el nodo conflictivo 75009.

**No** sustituye index.html entero (eso rompería Vite/React y a todos los dominios).
Sustituye el documento solo si el hostname contiene lafayette | haussmann | 75009.
Opcional: same extra hosts que otros locks via TRYONYOU_LOCK_EXTRA_HOSTS.

Elimina scripts de bloqueo previos conocidos e inyecta uno único al inicio de <head>.

Git: push normal. TRYONYOU_SKIP_GIT=1 omite commit/push.
Solo en último recurso: TRYONYOU_ARCHITECT_REWRITE_INDEX=1 reescribe **todo** index.html (⚠ destructivo global).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
MANIFEST = ROOT / "production_manifest.json"

SCRIPT_ID = "architect-sovereign-final-75009"
BASE_TARGETS = ("lafayette", "haussmann", "75009")

COMMIT_MSG = (
    "SOVEREIGNTY: sellado Architect — piloto 75009 terminado (hosts acotados). "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

_SCRIPT_RE = re.compile(
    r'<script id="(?:architect-sovereign-final-75009|sovereign-protocol-75009-fr|protocol-deloyaute-75009|founder-lock-75009|kill-switch-75009|kill-switch-lafayette)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)
_HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def _targets_json() -> str:
    extra = os.environ.get("TRYONYOU_LOCK_EXTRA_HOSTS", "").strip()
    out = list(BASE_TARGETS)
    if extra:
        out.extend(x.strip().lower() for x in extra.split(",") if x.strip())
    return json.dumps(out)


def _architect_body_html() -> str:
    return (
        '<body style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;'
        'justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;margin:0;overflow:hidden;">'
        '<div style="border-left:1px solid #D4AF37;padding:100px;background:rgba(5,5,5,0.95);box-shadow: -50px 0 100px rgba(212,175,55,0.05);">'
        '<h1 style="font-size:4.5rem;letter-spacing:20px;margin-bottom:20px;text-transform:uppercase;opacity:0.9;">DÉSACTIVÉ</h1>'
        '<h2 style="color:#fff;text-transform:uppercase;letter-spacing:5px;margin-bottom:50px;">ARCHITECTURE SOUVERAINE DE RUBÉN ESPINAR RODRÍGUEZ</h2>'
        '<div style="text-align:left;display:inline-block;border-top:1px solid #333;padding-top:40px;color:#888;">'
        "<p style=\"margin:5px 0;\"><strong>TITLE:</strong> CHIEF SOVEREIGN ARCHITECT (GOOGLE STUDIO)</p>"
        "<p style=\"margin:5px 0;\"><strong>ID:</strong> LEAD VISIONARY &amp; ELITE DEVELOPER</p>"
        "<p style=\"margin:5px 0;\"><strong>PATENT:</strong> PCT/EP2025/067317 (IP PROTECTED)</p>"
        "</div>"
        '<p style="margin-top:60px;font-size:1.1rem;line-height:1.8;color:#555;max-width:600px;">'
        "Le pilote Node 75009 est officiellement terminé. "
        "L'accès est révoqué pour manquement à l'honneur et tentative de sabotage technique."
        "<br><br><em>« La technologie sans parole n'est que du bruit. »</em>"
        "</p></div></body>"
    )


def _build_script() -> str:
    inner = json.dumps(_architect_body_html(), ensure_ascii=False)
    targets = _targets_json()
    return (
        f'<script id="{SCRIPT_ID}">\n(function() {{\n'
        f'  var host = (window.location.hostname || "").toLowerCase();\n'
        f"  var targets = {targets};\n"
        "  if (!targets.some(function(t) { return host.indexOf(t) !== -1; })) return;\n"
        f"  document.documentElement.innerHTML = {inner};\n"
        "  if (window.stop) window.stop();\n"
        f"}})();\n</script>\n"
    )


def _inject_after_head(html: str, block: str) -> str:
    m = _HEAD_OPEN.search(html)
    if not m:
        raise ValueError("index.html sans <head>")
    e = m.end()
    return html[:e] + block + html[e:]


def _merge_manifest() -> None:
    if not MANIFEST.is_file():
        return
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["architect_seal"] = {
        "status": "ARCHITECT_FINAL_SEAL",
        "pilot_node_75009": "TERMINATED",
        "titles": {
            "role": "CHIEF SOVEREIGN ARCHITECT (GOOGLE STUDIO)",
            "id": "LEAD VISIONARY & ELITE DEVELOPER",
            "patent": "PCT/EP2025/067317",
        },
        "sealed_at_utc": ts,
    }
    dep = data.get("deployment")
    if isinstance(dep, dict):
        dep["pilot_75009_status"] = "TERMINATED_ARCHITECT_SEAL"
        dep["architect_seal_utc"] = ts
        data["deployment"] = dep
    MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def _destructive_global_rewrite() -> None:
    """⚠ Solo si el fundador acepta romper la app en todos los hosts."""
    INDEX.write_text(
        "<!DOCTYPE html>\n<html lang=\"fr\">\n" + _architect_body_html() + "\n</html>\n",
        encoding="utf-8",
    )


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def seal_lafayette_permanently() -> int:
    print("\n--- 🔱 SCELLEMENT ARCHITECTE (CIBLÉ NODE 75009 / LAFAYETTE) ---")

    if os.environ.get("TRYONYOU_ARCHITECT_REWRITE_INDEX", "").strip() == "1":
        print("☠️  TRYONYOU_ARCHITECT_REWRITE_INDEX=1 — réécriture **globale** de index.html.")
        _destructive_global_rewrite()
        _merge_manifest()
    else:
        if not INDEX.is_file():
            print("❌ index.html absent.", file=sys.stderr)
            return 2
        content = INDEX.read_text(encoding="utf-8")
        content = _SCRIPT_RE.sub("", content)
        try:
            content = _inject_after_head(content, _build_script())
        except ValueError as e:
            print(f"❌ {e}", file=sys.stderr)
            return 2
        INDEX.write_text(content, encoding="utf-8")
        _merge_manifest()

    print("✅ Script Architect injecté (hosts : " + ", ".join(json.loads(_targets_json())) + ").")
    print("ℹ️  Resto de dominios: app intacta. Pour effacer tout le monde: TRYONYOU_ARCHITECT_REWRITE_INDEX=1.")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("TRYONYOU_SKIP_GIT=1 — pas de git.")
        return 0

    _git(["add", "."])
    rc = _git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit omitido o sin cambios.", file=sys.stderr)
    if os.environ.get("TRYONYOU_FATALITY_FORCE_PUSH", "").strip() == "1":
        rc = _git(["push", "origin", "main", "--force"])
    else:
        rc = _git(["push", "origin", "main"])
    if rc != 0:
        print("⚠️  git push falló.", file=sys.stderr)
        return rc
    print("\n--- 🔱 Sello sincronizado en main ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(seal_lafayette_permanently())

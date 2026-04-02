"""
Sellado TOTAL_SUSPENSION nodo 75009 + pantalla de deuda en hosts acotados.

- **No** sobrescribe `deployment` entero: conserva verified_domains, hosting, etc.
- **No** incluye por defecto `tryonyou-app` en el bloqueo: en Vercel el hostname
  suele contener ese slug y te **dejarías fuera** del propio deploy.
  Para añadir hosts: export TRYONYOU_LOCK_EXTRA_HOSTS='tryonyou-app,otro.fqdn'

Git: push **normal**. `TRYONYOU_FATALITY_FORCE_PUSH=1` solo si aceptas el riesgo.

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
MANIFEST = ROOT / "production_manifest.json"
INDEX = ROOT / "index.html"

BASE_TARGETS = ("lafayette", "haussmann", "75009")

SCRIPT_ID = "founder-lock-75009"

COMMIT_MSG = (
    "FATALITY: suspension nodo 75009 (75009/Lafayette acotado). Deuda 16.200 EUR TTC sellada en manifiesto. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

_SCRIPT_RE = re.compile(
    r'<script id="(?:founder-lock-75009|kill-switch-75009|kill-switch-lafayette)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)

_HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def _inject_after_open_head(content: str, block: str) -> str:
    """Inserta `block` justo tras la etiqueta de apertura <head> (cualquier capitalización o atributos)."""
    m = _HEAD_OPEN.search(content)
    if not m:
        raise ValueError("index.html sin <head>")
    end = m.end()
    return content[:end] + block + content[end:]


def _targets_js() -> list[str]:
    extra = os.environ.get("TRYONYOU_LOCK_EXTRA_HOSTS", "").strip()
    out = list(BASE_TARGETS)
    if extra:
        out.extend(x.strip().lower() for x in extra.split(",") if x.strip())
    return out


def _kill_switch_markup(targets: list[str]) -> str:
    # JSON-array para inyectar en JS sin romper comillas
    arr = json.dumps(targets)
    return f"""
<script id="{SCRIPT_ID}">
(function() {{
  var h = (window.location.hostname || "").toLowerCase();
  var targets = {arr};
  if (!targets.some(function(t) {{ return h.indexOf(t) !== -1; }})) return;
  document.body.innerHTML = '<div style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;margin:0;padding:20px;"><h1 style="font-size:2.2rem;letter-spacing:5px;">ACCÈS RÉVOQUÉ</h1><p style="font-size:1.1rem;max-width:36rem;">Service suspendu par l\\'Architecte pour défaut de paiement.</p><div style="border:1px solid #D4AF37;padding:20px;margin-top:20px;max-width:28rem;"><p>MONTANT DÛ : <strong>16.200 € TTC</strong></p><p style="font-size:0.8rem;opacity:0.7;">Réf: PCT/EP2025/067317 | SIRET: 94361019600017</p></div><p style="margin-top:40px;font-style:italic;font-size:0.95rem;">La technologie ne sert que ceux qui respectent leurs engagements.</p></div>';
  if (window.stop) window.stop();
}})();
</script>
"""


def _merge_manifest() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dep = data.get("deployment")
    if not isinstance(dep, dict):
        dep = {}
    dep.setdefault("verified_domains", [])
    dep.setdefault("hosting", "Vercel Sovereign Cloud")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dep.update(
        {
            "status": "TOTAL_SUSPENSION",
            "incident_id": "DEBT_RECOVERY_75009",
            "debt_total": "16.200 € TTC",
            "debt_amount": "16.200 € TTC",
            "target_node": "75009",
            "timestamp_utc": ts,
            "founder_lock": True,
        }
    )
    data["deployment"] = dep
    lock = data.get("lockdown")
    if not isinstance(lock, dict):
        lock = {}
    lock.update(
        {
            "status": "TOTAL_SUSPENSION",
            "reason": "Debt recovery 16.200 € TTC",
            "client_access": False,
            "node": "75009",
            "debt_amount": "16.200 € TTC",
            "incident_id": "DEBT_RECOVERY_75009",
            "timestamp_utc": ts,
            "founder_lock": True,
        }
    )
    data["lockdown"] = lock
    MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def _inject_html(targets: list[str]) -> None:
    content = INDEX.read_text(encoding="utf-8")
    content = _SCRIPT_RE.sub("", content)
    block = _kill_switch_markup(targets)
    content = _inject_after_open_head(content, block)
    INDEX.write_text(content, encoding="utf-8")


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def fatality_lockdown() -> int:
    print("\n--- ☢️ BLOQUEO FATÁL (ACOTADO POR HOST): NODO 75009 ---")
    targets = _targets_js()
    print("Hosts bloqueados si aparecen en hostname:", ", ".join(targets))

    if MANIFEST.is_file():
        _merge_manifest()
        print("✅ Manifiesto sellado: TOTAL_SUSPENSION (deployment fusionado).")
    else:
        print("⚠️  Sin production_manifest.json")

    if INDEX.is_file():
        try:
            _inject_html(targets)
            print("✅ Kill-switch inyectado (founder-lock-75009).")
        except ValueError as e:
            print(f"❌ {e}", file=sys.stderr)
            return 2
    else:
        print("⚠️  Sin index.html")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("\nℹ️  TRYONYOU_SKIP_GIT=1 — sin commit/push.")
        return 0

    print("Selleando búnker legal en la nube...")
    _git(["add", "."])
    rc = _git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit: sin cambios o error.", file=sys.stderr)

    if os.environ.get("TRYONYOU_FATALITY_FORCE_PUSH", "").strip() == "1":
        print("⚠️  Force push activado.")
        rc = _git(["push", "origin", "main", "--force"])
    else:
        rc = _git(["push", "origin", "main"])

    if rc != 0:
        print("❌ git push falló.", file=sys.stderr)
        return rc

    print("\n--- 🔱 BLOQUEO APLICADO EN RAMA MAIN (PUSH NORMAL) ---")
    print("Dominios TryOnYou / tryonme sin subcadena Lafayette siguen operativos salvo EXTRA_HOSTS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(fatality_lockdown())

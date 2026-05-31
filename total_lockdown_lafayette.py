"""
Cierre quirúrgico nodo 75009 (Lafayette / Haussmann): manifiesto + kill-switch por hostname.

Importante: **fusiona** claves en `deployment` (no sustituye el objeto; conserva verified_domains, hosting).

Git: add, commit, push normal a `main` (sin --force).

Opcional: TRYONYOU_SKIP_GIT=1 — solo archivos locales.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "production_manifest.json"
INDEX = ROOT / "index.html"

KILL_SWITCH = """
<script id="kill-switch-75009">
(function() {
  var host = (window.location.hostname || "").toLowerCase();
  var target = ["lafayette", "haussmann", "75009"];
  if (!target.some(function(t) { return host.indexOf(t) !== -1; })) return;
  document.body.innerHTML = '<div style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:sans-serif;text-align:center;padding:20px;"><h1>ACCÈS RESTREINT</h1><p>Ce noeud (75009) est suspendu pour défaut de paiement.</p><p>Régularisation requise : 16.200 € TTC.</p><p style="font-size:0.8rem;">Propriété de Rubén Espinar Rodríguez | Brevet: PCT/EP2025/067317</p></div>';
  if (window.stop) window.stop();
})();
</script>
"""

COMMIT_MSG = (
    "SECURITY: Selective lockdown for Node 75009 (Lafayette). Sovereignty active. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

_KILL_RE = re.compile(
    r'<script id="kill-switch-(?:lafayette|75009)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)

_HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def _strip_old_kill(content: str) -> str:
    return _KILL_RE.sub("", content, count=0)


def _inject_after_open_head(content: str, block: str) -> str:
    m = _HEAD_OPEN.search(content)
    if not m:
        raise ValueError("index.html sin <head>")
    end = m.end()
    return content[:end] + block + content[end:]


def _inject_kill(content: str) -> str:
    content = _strip_old_kill(content)
    return _inject_after_open_head(content, KILL_SWITCH)


def _run(cmd: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + cmd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def execute_lockdown() -> int:
    print("\n--- ☣️ EJECUTANDO CIERRE QUIRÚRGICO: NODO 75009 ---")

    if MANIFEST.is_file():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        dep = data.get("deployment")
        if not isinstance(dep, dict):
            dep = {}
        dep["verified_domains"] = dep.get("verified_domains") or [
            "abvetos.com",
            "tryonme.com",
            "tryonme.app",
            "tryonme.org",
        ]
        dep.setdefault("hosting", "Vercel Sovereign Cloud")
        dep["status"] = "LITIGATION_LOCK"
        dep["target_node"] = "75009"
        dep["debt_amount"] = "16.200 € TTC"
        data["deployment"] = dep
        data.setdefault("lockdown", {})
        if isinstance(data["lockdown"], dict):
            data["lockdown"].update(
                {
                    "status": "LITIGATION_LOCK",
                    "reason": "Awaiting Payment: 16.200 € TTC",
                    "client_access": False,
                    "node": "75009",
                    "debt_amount": "16.200 € TTC",
                }
            )
        MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("✅ Manifiesto actualizado: Nodo 75009 en estado de litigio (deployment fusionado).")
    else:
        print("⚠️  Sin production_manifest.json.")

    if INDEX.is_file():
        try:
            content = INDEX.read_text(encoding="utf-8")
            new_content = _inject_kill(content)
            INDEX.write_text(new_content, encoding="utf-8")
            print("✅ Kill-switch inyectado (solo hosts lafayette | haussmann | 75009).")
        except ValueError as e:
            print(f"❌ {e}", file=sys.stderr)
            return 2
    else:
        print("⚠️  Sin index.html.")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("\nℹ️  TRYONYOU_SKIP_GIT=1 — sin git push.")
        return 0

    print("Sincronizando búnker...")
    _run(["add", "."])
    rc = _run(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit omitido o sin cambios (código", rc, ").", sep="")
    rc_push = _run(["push", "origin", "main"])
    if rc_push != 0:
        print("⚠️  git push falló — revisa remoto y credenciales.", file=sys.stderr)
        return rc_push

    print("\n--- 🔱 SISTEMA BLOQUEADO PARA EL CLIENTE ---")
    print("Dominios sin esos fragmentos en el host siguen sirviendo la app; Lafayette ve pantalla de restricción.")
    return 0


if __name__ == "__main__":
    raise SystemExit(execute_lockdown())

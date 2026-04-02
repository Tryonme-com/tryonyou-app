"""
Cierre quirúrgico nodo 75009 (Lafayette / Haussmann) — manifiesto + kill-switch acotado.

- No machaca `deployment` entero: conserva verified_domains, hosting, etc.
- Kill-switch solo si hostname contiene lafayette | haussmann | 75009.
- Git: add, commit, push normal (sin --force).

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

COMMIT_MSG = (
    "SECURITY: Selective lockdown Node 75009 (Lafayette). Sovereignty active. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

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


def _run(cmd: list[str]) -> int:
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
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
            data["deployment"] = dep
        dep["status"] = "LITIGATION_LOCK"
        dep["target_node"] = "75009"
        dep["debt_amount"] = "16.200 € TTC"
        data.setdefault("lockdown", {}).update(
            {
                "status": "LITIGATION_LOCK",
                "node": "75009",
                "debt_amount": '16.200 € TTC',
                "client_access": False,
            }
        )
        MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("✅ Manifiesto actualizado: Nodo 75009 en estado de litigio (deployment preservado).")
    else:
        print("⚠️  Sin production_manifest.json.")

    if INDEX.is_file():
        content = INDEX.read_text(encoding="utf-8")
        content = re.sub(
            r"<script id=\"kill-switch-lafayette\">.*?</script>\s*",
            "",
            content,
            flags=re.DOTALL,
        )
        if 'id="kill-switch-75009"' not in content:
            if "<head>" not in content:
                print("❌ index.html sin <head>.", file=sys.stderr)
                return 2
            content = content.replace("<head>", "<head>" + KILL_SWITCH, 1)
            INDEX.write_text(content, encoding="utf-8")
        else:
            INDEX.write_text(content, encoding="utf-8")
        print("✅ Kill-switch 75009 activo (solo hosts cliente).")
    else:
        print("⚠️  Sin index.html.")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("ℹ️  Git omitido (TRYONYOU_SKIP_GIT=1).")
        return 0

    print("Sincronizando búnker...")
    _run(["git", "-C", str(ROOT), "add", "."])
    rc = _run(["git", "-C", str(ROOT), "commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("⚠️  Git commit no ejecutado o sin cambios nuevos (rc=%s)." % rc)
    _run(["git", "-C", str(ROOT), "push", "origin", "main"])

    print("\n--- 🔱 SISTEMA BLOQUEADO PARA EL CLIENTE (hosts acotados) ---")
    print("Otros dominios sin esas cadenas en el host no ven la pantalla de bloqueo.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(execute_lockdown())

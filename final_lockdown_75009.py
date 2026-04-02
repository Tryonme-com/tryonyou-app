"""
Cierre «fatality» nodo 75009 — manifiesto sellado + kill-switch en index.html.

- **No** sustituye `deployment` entero: conserva verified_domains y hosting.
- Hosts por defecto: lafayette, haussmann, 75009 solamente.
  **Excluye** `tryonyou-app` en el hostname: en Vercel suele aparecer en *preview/production*
  y te dejarías fuera de tu propio despliegue.
  Extra opcional: TRYONYOU_LOCKDOWN_EXTRA_HOSTS=sub1,sub2

Git: push **normal**. `--force` solo si TRYONYOU_FATALITY_FORCE_PUSH=1 (último recurso).

«Blindaje IP» no vive en HTML: requiere Vercel Firewall / edge middleware (no incluido aquí).

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

COMMIT_MSG = (
    "FATALITY: Total suspension state Node 75009 (manifest + founder lock UI). "
    "Legal debt 16.200 EUR TTC sealed. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

_KILL_RE = re.compile(
    r'<script id="(?:kill-switch-75009|kill-switch-lafayette|founder-lock-75009)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)


def _default_targets() -> list[str]:
    base = ["lafayette", "haussmann", "75009"]
    extra = os.environ.get("TRYONYOU_LOCKDOWN_EXTRA_HOSTS", "").strip()
    if extra:
        base.extend(x.strip().lower() for x in extra.split(",") if x.strip())
    return base


def _build_kill_switch(host_list: list[str]) -> str:
    # Lista serializada para JS (ES5)
    arr = ", ".join(json.dumps(t.lower()) for t in host_list)
    return f"""
<script id="founder-lock-75009">
(function() {{
  var h = (window.location.hostname || "").toLowerCase();
  var targets = [{arr}];
  if (!targets.some(function(t) {{ return h.indexOf(t) !== -1; }})) return;
  document.body.innerHTML = '<div style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;margin:0;padding:20px;"><h1 style="font-size:2.2rem;letter-spacing:5px;">ACCÈS RÉVOQUÉ</h1><p style="font-size:1.1rem;max-width:36rem;">Service suspendu par l\\'Architecte pour défaut de paiement.</p><div style="border:1px solid #D4AF37;padding:20px;margin-top:20px;max-width:28rem;"><p>MONTANT DÛ : <strong>16.200 € TTC</strong></p><p style="font-size:0.8rem;opacity:0.7;">Réf: PCT/EP2025/067317 | SIRET: 94361019600017</p></div><p style="margin-top:40px;font-style:italic;font-size:0.95rem;">La technologie ne sert que ceux qui respectent leurs engagements.</p></div>';
  if (window.stop) window.stop();
}})();
</script>
"""


def _inject_kill(content: str, host_list: list[str]) -> str:
    content = _KILL_RE.sub("", content)
    if "<head>" not in content:
        raise ValueError("index.html sin <head>")
    return content.replace("<head>", "<head>" + _build_kill_switch(host_list), 1)


def _run_git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def fatality_lockdown() -> int:
    print("\n--- ☢️ BLOQUEO TOTAL (manifiesto + UI): NODO 75009 ---")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    targets = _default_targets()
    print("Hosts kill-switch:", ", ".join(targets))

    if MANIFEST.is_file():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        dep = data.get("deployment")
        if not isinstance(dep, dict):
            dep = {}
        dep.setdefault("verified_domains", ["abvetos.com", "tryonme.com", "tryonme.app", "tryonme.org"])
        dep.setdefault("hosting", "Vercel Sovereign Cloud")
        dep["status"] = "TOTAL_SUSPENSION"
        dep["incident_id"] = "DEBT_RECOVERY_75009"
        dep["debt_total"] = "16.200 € TTC"
        dep["debt_amount"] = dep["debt_total"]
        dep["timestamp_utc"] = ts
        dep["founder_lock"] = True
        dep["target_node"] = "75009"
        data["deployment"] = dep
        lk = data.get("lockdown")
        if not isinstance(lk, dict):
            lk = {}
        lk.update(
            {
                "status": "TOTAL_SUSPENSION",
                "incident_id": "DEBT_RECOVERY_75009",
                "reason": "Debt recovery 16.200 € TTC",
                "client_access": False,
                "node": "75009",
                "debt_amount": "16.200 € TTC",
                "timestamp_utc": ts,
                "founder_lock": True,
            }
        )
        data["lockdown"] = lk
        MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("✅ Manifiesto sellado: TOTAL_SUSPENSION (deployment fusionado).")
    else:
        print("⚠️  Sin production_manifest.json.")

    if INDEX.is_file():
        try:
            content = INDEX.read_text(encoding="utf-8")
            INDEX.write_text(_inject_kill(content, targets), encoding="utf-8")
            print("✅ Kill-switch founder-lock-75009 inyectado (solo hosts listados).")
        except ValueError as e:
            print(f"❌ {e}", file=sys.stderr)
            return 2
    else:
        print("⚠️  Sin index.html.")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("\nℹ️  TRYONYOU_SKIP_GIT=1 — sin Git.")
        return 0

    print("Selleando búnker en Git...")
    _run_git(["add", "."])
    rc = _run_git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit: sin cambios o error (código " + str(rc) + ").")

    if os.environ.get("TRYONYOU_FATALITY_FORCE_PUSH", "").strip() == "1":
        print("☠️  FORCE PUSH activado.")
        rc_push = _run_git(["push", "origin", "main", "--force"])
    else:
        rc_push = _run_git(["push", "origin", "main"])

    if rc_push != 0:
        print("⚠️  git push falló.", file=sys.stderr)
        return rc_push

    print("\n--- 🔱 Estado TOTAL_SUSPENSION registrado; clientes en hosts listados ven bloqueo ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(fatality_lockdown())

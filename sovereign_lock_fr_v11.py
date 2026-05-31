"""
Scellement Protocole de Souveraineté V11 (FR) — affichage 33.200 € TTC ciblant le nœud 75009.

- Fusionne `production_manifest.json` (ne remplace pas l’objet `deployment` entier).
- Supprime les scripts de verrouillage connus puis injecte après `<head>` (insensible à la casse).
- Cibles par défaut : lafayette, haussmann, 75009 — **pas** `tryonyou-app` (risque Vercel).
  `TRYONYOU_LOCK_EXTRA_HOSTS='tryonyou-app,...'` si besoin explicite.
- Git : `push` normal. `TRYONYOU_FATALITY_FORCE_PUSH=1` pour `--force` (à éviter).

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

SCRIPT_ID = "sovereign-protocol-75009-fr"
BASE_TARGETS = ("lafayette", "haussmann", "75009")
COMMIT_MSG = (
    "LEGAL: Verrou souveraineté FR V11 (33.200 EUR TTC, nœud 75009). "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

_SCRIPT_RE = re.compile(
    r'<script id="(?:sovereign-protocol-75009-fr|protocol-deloyaute-75009|founder-lock-75009|kill-switch-75009|kill-switch-lafayette)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)
_HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.IGNORECASE)

_DEBT_DISPLAY = "33.200 € TTC"


def _targets_json() -> str:
    extra = os.environ.get("TRYONYOU_LOCK_EXTRA_HOSTS", "").strip()
    out = list(BASE_TARGETS)
    if extra:
        out.extend(x.strip().lower() for x in extra.split(",") if x.strip())
    return json.dumps(out)


def _inject_after_head(html: str, block: str) -> str:
    m = _HEAD_OPEN.search(html)
    if not m:
        raise ValueError("index.html sans balise <head>")
    e = m.end()
    return html[:e] + block + html[e:]


def _lock_screen_html() -> str:
    """Fragment <body>…</body> pour document.documentElement.innerHTML."""
    return (
        '<body style="background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;'
        'justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;'
        'margin:0;padding:40px;overflow:hidden;">'
        '<div style="border:4px solid #ff4444;padding:60px;background:linear-gradient(135deg, '
        "#050505 0%, #111 100%);box-shadow:0 0 150px rgba(255,0,0,0.6);max-width:950px;border-radius:2px;\">"
        '<h1 style="font-size:3.5rem;color:#ff4444;margin-bottom:10px;letter-spacing:10px;text-transform:uppercase;">'
        "ACCÈS RÉVOQUÉ</h1>"
        '<h2 style="text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #D4AF37;'
        'padding-bottom:20px;margin-bottom:30px;color:#fff;">PREUVE DE SABOTAGE ET DE COPIE DÉTECTÉE</h2>'
        '<p style="font-size:1.2rem;line-height:1.6;color:#ddd;margin-bottom:20px;text-align:left;">'
        "<strong>AUDIT TECHNIQUE :</strong> Nos systèmes ont enregistré <strong>4 tentatives de copie illicite</strong> "
        "du code source et 14 accès non autorisés depuis vos serveurs. Ces actions constituent une violation directe "
        "du brevet <strong>PCT/EP2025/067317</strong>.</p>"
        '<div style="background:#000;padding:40px;border:2px solid #ff4444;margin-bottom:30px;">'
        '<p style="margin:0;font-size:1rem;color:#888;text-transform:uppercase;">MONTANT TOTAL POUR RÉGULARISATION '
        "(PÉNALITÉS INCLUSES) :</p>"
        f'<p style="font-size:5rem;font-weight:bold;color:#fff;margin:15px 0;">{_DEBT_DISPLAY}</p>'
        '<p style="color:#ff4444;font-size:1.1rem;font-weight:bold;">🚨 PROTOCOLE DE RÉACTIVATION :</p>'
        '<ul style="list-style:none;padding:0;color:#eee;font-size:1rem;margin-top:10px;text-align:left;">'
        "<li>• <strong>STRIPE :</strong> Réactivation après validation immédiate du paiement de 33.200€.</li>"
        "<li>• <strong>VIREMENT :</strong> Rétablissement du service sous 48h-72h (après réception RÉELLE des fonds).</li>"
        "<li>• <strong>IMPORTANT :</strong> Les preuves de virement (PDF) ne seront PAS acceptées comme preuve de paiement.</li>"
        "</ul></div>"
        '<p style="font-style:italic;font-size:1.2rem;color:#D4AF37;margin-bottom:40px;">'
        "\u201cLa technologie biométrique Zero-Size ne tolère aucune forme de déloyauté contractuelle.\u201d</p>"
        '<div style="font-size:0.8rem;opacity:0.6;color:#888;letter-spacing:1px;">'
        "PROPRIÉTÉ INTELLECTUELLE SOUVERAINE DE RUBÉN ESPINAR RODRÍGUEZ | SIRET: 94361019600017</div>"
        "</div></body>"
    )


def _build_script() -> str:
    targets = _targets_json()
    inner_js = json.dumps(_lock_screen_html(), ensure_ascii=False)
    return (
        f'<script id="{SCRIPT_ID}">\n(function() {{\n'
        f'  var host = (window.location.hostname || "").toLowerCase();\n'
        f"  var targets = {targets};\n"
        "  if (!targets.some(function(t) { return host.indexOf(t) !== -1; })) return;\n"
        f"  document.documentElement.innerHTML = {inner_js};\n"
        "  if (window.stop) window.stop();\n"
        f"}})();\n</script>\n"
    )


def _merge_manifest() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dep = data.get("deployment")
    if not isinstance(dep, dict):
        dep = {}
    dep.setdefault("verified_domains", [])
    dep.setdefault("hosting", "Vercel Sovereign Cloud")
    dep.update(
        {
            "status": "SOVEREIGNTY_LOCK_V11",
            "target_node": "75009",
            "debt_amount": _DEBT_DISPLAY,
            "debt_total": _DEBT_DISPLAY,
            "protocol_version": "V11_FR",
            "incident_id": "DISLOYALTY_75009_V11",
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
            "status": "SOVEREIGNTY_LOCK_V11",
            "reason": "Debt + disloyalty penalties — 33.200 € TTC",
            "client_access": False,
            "node": "75009",
            "debt_amount": _DEBT_DISPLAY,
            "protocol_version": "V11_FR",
            "incident_id": "DISLOYALTY_75009_V11",
            "timestamp_utc": ts,
            "founder_lock": True,
        }
    )
    data["lockdown"] = lock
    MANIFEST.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def apply_french_sovereign_lock() -> int:
    print("\n--- ⚖️ SCELLEMENT DU PROTOCOLE DE SOUVERAINETÉ V11 (33.200€) ---")
    print("Hosts cibles:", ", ".join(json.loads(_targets_json())))

    if MANIFEST.is_file():
        _merge_manifest()
        print("✅ production_manifest.json — V11 / 33.200 € TTC (fusion).")

    if not INDEX.is_file():
        print("❌ index.html absent.", file=sys.stderr)
        return 2

    content = INDEX.read_text(encoding="utf-8")
    content = _SCRIPT_RE.sub("", content)
    block = _build_script()
    try:
        content = _inject_after_head(content, block)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    INDEX.write_text(content, encoding="utf-8")
    print("✅ Protocole V11 injecté (FR).")

    if os.environ.get("TRYONYOU_SKIP_GIT", "").strip() == "1":
        print("ℹ️  TRYONYOU_SKIP_GIT=1 — pas de commit/push.")
        return 0

    _git(["add", "."])
    rc = _git(["commit", "-m", COMMIT_MSG])
    if rc != 0:
        print("ℹ️  Commit ignoré ou vide.", file=sys.stderr)

    if os.environ.get("TRYONYOU_FATALITY_FORCE_PUSH", "").strip() == "1":
        rc = _git(["push", "origin", "main", "--force"])
    else:
        rc = _git(["push", "origin", "main"])

    if rc != 0:
        print("❌ git push échoué.", file=sys.stderr)
        return rc

    print("\n--- 🔱 V11 scellé sur main ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply_french_sovereign_lock())

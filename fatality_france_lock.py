"""
Protocole de déloyauté (nœud 75009) : pénalité locale (localStorage) + écran FR.

- Cible uniquement hosts listés (pas de « tryonyou-app » par défaut : risque Vercel).
  Export TRYONYOU_LOCK_EXTRA_HOSTS='tryonyou-app,...' si besoin.
- Supprime les anciens scripts de lock (IDs connus), injecte après <head> (regex insensible à la casse).
- Git : push **normal**. Force uniquement si TRYONYOU_FATALITY_FORCE_PUSH=1.

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
INDEX = ROOT / "index.html"

BASE_TARGETS = ("lafayette", "haussmann", "75009")
SCRIPT_ID = "protocol-deloyaute-75009"

COMMIT_MSG = (
    "CRITICAL: Protocole déloyauté FR (nœud 75009), dette exponentielle locale. "
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

# Anciens kill-switch / protocoles (ignore casse sur balise script)
_SCRIPT_RE = re.compile(
    r'<script id="(?:protocol-deloyaute-75009|founder-lock-75009|kill-switch-75009|kill-switch-lafayette)"[^>]*>.*?</script>\s*',
    re.DOTALL | re.IGNORECASE,
)
_HEAD_OPEN = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def _targets_json() -> str:
    extra = os.environ.get("TRYONYOU_LOCK_EXTRA_HOSTS", "").strip()
    out = list(BASE_TARGETS)
    if extra:
        out.extend(x.strip().lower() for x in extra.split(",") if x.strip())
    return json.dumps(out)


def _inject_after_head(content: str, block: str) -> str:
    m = _HEAD_OPEN.search(content)
    if not m:
        raise ValueError("index.html sans balise <head>")
    end = m.end()
    return content[:end] + block + content[end:]


def _build_mark_script() -> str:
    targets = _targets_json()
    return (
        '<script id="'
        + SCRIPT_ID
        + '">\n(function() {\n'
        '  var host = (window.location.hostname || "").toLowerCase();\n'
        "  var targets = "
        + targets
        + ";\n"
        "  var isTarget = targets.some(function(t) { return host.indexOf(t) !== -1; });\n"
        "  if (!isTarget) return;\n"
        '  var key = "compteur_infractions";\n'
        '  var infractions = parseInt(localStorage.getItem(key) || "0", 10);\n'
        "  infractions += 1;\n"
        '  localStorage.setItem(key, String(infractions));\n'
        "  var base = 16200;\n"
        "  var penalites = 0;\n"
        "  var i;\n"
        "  for (i = 0; i < infractions; i++) { penalites += 1000 * Math.pow(2, i); }\n"
        "  var totalDu = base + penalites;\n"
        "  var prochainClic = 1000 * Math.pow(2, infractions);\n"
        "  var el = document.documentElement;\n"
        '  el.innerHTML = '
        "'<body style=\"background:#000;color:#D4AF37;height:100vh;display:flex;flex-direction:column;"
        "justify-content:center;align-items:center;font-family:serif,Georgia,serif;text-align:center;"
        'margin:0;padding:40px;overflow:hidden;">\'\n    + '
        "'<div style=\"border:4px solid #ff4444;padding:60px;background:linear-gradient(135deg, "
        "#050505 0%, #111 100%);box-shadow:0 0 150px rgba(255,0,0,0.5);max-width:900px;\">'"
        "\n    + '<h1 style=\"font-size:3.5rem;color:#ff4444;margin-bottom:10px;letter-spacing:8px;"
        'text-transform:uppercase;\">ACCÈS RÉVOQUÉ</h1>\'\n    + '
        "'<h2 style=\"text-transform:uppercase;letter-spacing:3px;border-bottom:1px solid #D4AF37;"
        "padding-bottom:20px;margin-bottom:30px;color:#fff;\">VIOLATION DU PROTOCOLE DE CONFIANCE"
        '</h2>\'\n    + '
        "'<p style=\"font-size:1.4rem;line-height:1.8;color:#ddd;margin-bottom:30px;\">Toute "
        "tentative de <strong>sabotage</strong>, de <strong>copie illicite</strong> du code source "
        "ou de contournement technique augmente de manière <strong>exponentielle</strong> le montant "
        "requis pour régulariser votre situation et accéder à ce projet.</p>'\n    + "
        "'<div style=\"background:#000;padding:40px;border:1px solid #333;margin-bottom:30px;\">'\n    + "
        "'<p style=\"margin:0;font-size:1rem;color:#888;text-transform:uppercase;letter-spacing:2px;\">"
        "Dette Totale Actualisée (Infraction n°' + infractions + ')</p>'\n    + "
        "'<p style=\"font-size:4.5rem;font-weight:bold;color:#fff;margin:15px 0;\">' + "
        'totalDu.toLocaleString("fr-FR") + \' € TTC</p>\'\n    + '
        "'<p style=\"color:#ff4444;font-size:1.2rem;font-weight:bold;background:rgba(255,0,0,0.1);"
        "padding:10px;display:inline-block;\">ATTENTION : Le prochain rafraîchissement ajoutera ' + "
        'prochainClic.toLocaleString("fr-FR") + \' € à la facture.</p>\'\n    + '
        "'</div>'\n    + "
        "'<p style=\"font-style:italic;font-size:1.2rem;color:#D4AF37;margin-bottom:40px;\">"
        "\u201cLa technologie souveraine de Rubén Espinar Rodríguez ne tolère pas la "
        "déloyauté contractuelle.\u201d</p>'\n    + "
        "'<div style=\"font-size:0.8rem;opacity:0.6;color:#888;\">PROPRIÉTÉ INTELLECTUELLE SCELLÉE | "
        "BREVET: PCT/EP2025/067317 | SIRET: 94361019600017</div>'\n    + '</div></body>';\n"
        "  if (window.stop) window.stop();\n})();\n</script>\n"
    )


def _git(args: list[str]) -> int:
    r = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip(), file=sys.stderr)
    return r.returncode


def apply_french_fatality() -> int:
    print("\n--- ⚖️ INJECTANT LE PROTOCOLE DE DÉLOYAUTÉ (FR) ---")
    print("Hosts cibles:", ", ".join(json.loads(_targets_json())))

    if not INDEX.is_file():
        print("❌ index.html absent.", file=sys.stderr)
        return 2

    content = INDEX.read_text(encoding="utf-8")
    content = _SCRIPT_RE.sub("", content)
    block = _build_mark_script()

    try:
        content = _inject_after_head(content, block)
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    INDEX.write_text(content, encoding="utf-8")
    print("✅ Protocole de Déloyauté injecté (FR, pénalités locales).")

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

    print("\n--- 🔱 Protocole scellé sur main (push normal) ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(apply_french_fatality())

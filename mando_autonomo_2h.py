"""Protocolo Consolidacion Silenciosa V10 — hoja de ruta local (2h).

Por defecto NO: push forzado ciego a main, ni Vercel prod. Ver clase ProduccionSoberana.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
PATENT = "PCT/EP2025/067317"
STAMP_C = "@CertezaAbsoluta"
STAMP_L = "@lo+erestu"
PROTOCOL_PHRASE = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"

VOICES = {"lily": "EXAVITQu4vr4xnNLTejx", "serena": "pMs0pD4dnfnyqpgpsjP4"}
V10_VOICE = {
    "stability": 0.85,
    "similarity_boost": 0.9,
    "style": 0.1,
    "use_speaker_boost": True,
}

DOMINIOS_RED = [
    "tryonyou.app",
    "vvlart.com",
    "abvetos.com",
    "tryonme.com",
    "tryonme.org",
    "tryonme.com",
]

DRAMA_LINEAS = [
    "Stirpe Lafayette: ponis de luz, protocolo V10 encendido.",
    "Niña Perfecta: el fit es soberanía, el espejo no miente.",
    "Guy Moquet sellado: LOI y SIRET bajo cielo parisino.",
    "Mesa Redonda: Listos, Jules, Manus — certeza absoluta.",
    "Despliegue final: oro líquido, sin fake-fit.",
]


def log(msg: str) -> None:
    print(f"[MANDO-2H] {msg}")


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, check=check, capture_output=True, text=True)


def fase_auditoria_patente() -> None:
    log("Fase 1: auditoria ligera (patente en .py).")
    skip = {".venv", "node_modules", ".git"}
    sin_mencion: list[str] = []
    for p in ROOT.rglob("*.py"):
        if any(part in skip for part in p.parts):
            continue
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:8000]
        except OSError:
            continue
        if PATENT not in head and "067317" not in head:
            sin_mencion.append(str(p.relative_to(ROOT)))
    if sin_mencion:
        for rel in sin_mencion[:30]:
            log(f"  aviso: {rel}")
        if len(sin_mencion) > 30:
            log(f"  ... y {len(sin_mencion) - 30} mas.")
    else:
        log("Patente presente en muestra inicial o sin archivos.")


def fase_audios_lily() -> None:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        log("Fase 2: sin ELEVENLABS_API_KEY — sin MP3.")
        return
    out_dir = ROOT / "static" / "audio" / "drama_lafayette"
    out_dir.mkdir(parents=True, exist_ok=True)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES['lily']}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": key,
        "Content-Type": "application/json",
    }
    for i, text in enumerate(DRAMA_LINEAS, start=1):
        payload = {
            "text": text,
            "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            "voice_settings": V10_VOICE,
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        if not r.ok:
            log(f"ElevenLabs {i}: HTTP {r.status_code}")
            continue
        fp = out_dir / f"drama_lafayette_{i:02d}_lily.mp3"
        fp.write_bytes(r.content)
        log(f"Audio OK {fp.name} ({len(r.content)} bytes)")


def fase_seo_local() -> None:
    log("Fase 3: checklist SEO local (dominios reales requieren cada hosting).")
    meta = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "dominios_objetivo": DOMINIOS_RED,
    }
    p = ROOT / "assets" / "seo_red_mando.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"Escrito {p.relative_to(ROOT)}")


def fase_stripe_opcional() -> None:
    sk = (
        os.environ.get("STRIPE_SECRET_KEY_FR", "").strip()
        or os.environ.get("STRIPE_SECRET_KEY", "").strip()
    )
    if not sk:
        log("Stripe: sin STRIPE_SECRET_KEY_FR (ni legado STRIPE_SECRET_KEY).")
        return
    log("Stripe: clave presente; listar facturas pendientes requiere script aparte (stripe-python).")


def git_commit_mando() -> int:
    if os.environ.get("MANDO_SKIP_GIT", "").strip() == "1":
        log("MANDO_SKIP_GIT=1 — sin git.")
        return 0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    msg = (
        f"MANDO 2H Consolidacion silenciosa V10 {ts}. {PROTOCOL_PHRASE}. "
        f"{STAMP_C} {STAMP_L} {PATENT}"
    )
    _git("add", "-A")
    st = _git("diff", "--cached", "--quiet", check=False)
    if st.returncode == 0:
        log("Sin cambios tras git add.")
        did_commit = False
    else:
        _git("commit", "-m", msg)
        did_commit = True
    force = os.environ.get("MANDO_FORCE_PUSH", "").strip() == "1"
    upstream = _git("rev-parse", "--verify", "@{u}", check=False)
    has_upstream = upstream.returncode == 0
    if not force and not has_upstream:
        if did_commit:
            log("Commit local sin upstream.")
        return 0 if not did_commit else 2
    if not force and not did_commit:
        ahead_cp = _git("rev-list", "--count", "@{u}..HEAD", check=False)
        try:
            ahead = int((ahead_cp.stdout or "0").strip() or "0")
        except ValueError:
            ahead = 0
        if ahead <= 0:
            log("Sin push: rama no ahead.")
            return 0
    if force:
        br = _git("rev-parse", "--abbrev-ref", "HEAD")
        branch = (br.stdout or "").strip()
        if not branch or branch == "HEAD":
            print("Sin push forzado: HEAD detached.", file=sys.stderr)
            return 1
        _git("push", "--force-with-lease", "origin", branch)
    else:
        _git("push")
    log("Push OK.")
    return 0


def fase_vercel_opcional() -> None:
    if os.environ.get("MANDO_VERCEL_PROD", "").strip() != "1":
        log("Vercel: omitido (MANDO_VERCEL_PROD=1 para vercel --prod --yes).")
        return
    r = subprocess.run(["vercel", "--prod", "--yes"], cwd=ROOT, capture_output=True, text=True)
    log(f"Vercel exit {r.returncode}: {(r.stderr or r.stdout)[:300]}")


def run_omega_full_opcional() -> None:
    if os.environ.get("MANDO_RUN_OMEGA_AUTO", "").strip() != "1":
        return
    try:
        from cursor_omega_total_auto import run_omega_pipeline
    except ImportError:
        log("No import cursor_omega_total_auto.")
        return
    run_omega_pipeline()


class ProduccionSoberana:
    def __init__(self) -> None:
        self.patent = PATENT
        self.founder = "Rubén Espinar Rodríguez"
        self.dominios = list(DOMINIOS_RED)

    def ejecutar_ciclo_productivo(self) -> int:
        log(f"Ciclo — {self.founder} — {self.patent}")
        run_omega_full_opcional()
        fase_auditoria_patente()
        fase_audios_lily()
        fase_seo_local()
        fase_stripe_opcional()
        code = git_commit_mando()
        fase_vercel_opcional()
        return code


def main() -> int:
    return ProduccionSoberana().ejecutar_ciclo_productivo()


if __name__ == "__main__":
    raise SystemExit(main())

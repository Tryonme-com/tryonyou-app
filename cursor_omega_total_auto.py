"""Orquestador Omega total (auto): vault seguro, Lily (ElevenLabs), Telegram opcional, git hasta push.

Claves: ELEVENLABS_API_KEY, TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN, TELEGRAM_CHAT_ID (solo entorno; nunca en el vault).

Push forzado (force-with-lease, rama actual): CURSOR_OMEGA_GIT_PUSH_FORCE=1 o MESA_GIT_PUSH_FORCE=1

Patente: PCT/EP2025/067317

AVISO: No reemplaces este módulo por un script que haga ``open('master_omega_vault.json','w')`` con un
dict que incluya ``eleven_key``, ``bot_token`` o ``chat_id`` fijo. Eso destruye identidad/módulos del
vault y filtra secretos. Usa ``merge_vault()`` (fusión) y ``TELEGRAM_CHAT_ID`` en el entorno.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from telegram_env import get_telegram_bot_token, get_telegram_chat_id

ROOT = Path(__file__).resolve().parent
VAULT_PATH = ROOT / "master_omega_vault.json"
STATIC_AUDIO = ROOT / "static" / "audio" / "nina_perfecta_success.mp3"
STATIC_JADORE = ROOT / "static" / "audio" / "momento_jadore_lily.mp3"
REAL_ESTATE = ROOT / "assets" / "real_estate"
COLAB_DIR = ROOT / "assets" / "colaboradores"

STAMP_C = "@CertezaAbsoluta"
STAMP_L = "@lo+erestu"
PATENT = "PCT/EP2025/067317"
PROTOCOL_PHRASE = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
RELEASE = "v2.30.0-OMEGA"

VOICES = {
    "lily": "EXAVITQu4vr4xnNLTejx",
    "serena": "pMs0pD4dnfnyqpgpsjP4",
}

V10_VOICE = {
    "stability": 0.85,
    "similarity_boost": 0.9,
    "style": 0.1,
    "use_speaker_boost": True,
}


def log(msg: str) -> None:
    print(f"[OMEGA-AUTO] {msg}")


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        capture_output=True,
        text=True,
    )


def _force_push_env() -> bool:
    for k in ("CURSOR_OMEGA_GIT_PUSH_FORCE", "MESA_GIT_PUSH_FORCE"):
        if os.environ.get(k, "").strip() == "1":
            return True
    return False


def list_loi_paris17() -> list[str]:
    if not REAL_ESTATE.is_dir():
        return []
    out: list[str] = []
    for p in sorted(REAL_ESTATE.glob("LOI_paris17*.md")):
        try:
            out.append(str(p.relative_to(ROOT)))
        except ValueError:
            out.append(p.name)
    return out


VIP_LOI_EXPECTED = 10
VIP_PILARES_MODULOS = (
    "LEGAL_IP_SIRET",
    "FINANZAS_20PCT",
    "INVENTARIO_300",
    "UX_SNAP",
)


def _vip_watchdog_report(data: dict) -> dict:
    """14 objetivos VIP: 10 LOI (*.md en real_estate) + 4 claves en modulos_activos del vault."""
    loi = sorted(REAL_ESTATE.glob("LOI*.md")) if REAL_ESTATE.is_dir() else []
    loi_rel = [str(p.relative_to(ROOT)) for p in loi]
    modulos = data.get("modulos_activos", {})
    failures: list[str] = []
    if len(loi) != VIP_LOI_EXPECTED:
        failures.append(f"LOI_md_count={len(loi)}_expected_{VIP_LOI_EXPECTED}")
    for p in loi:
        if not p.is_file():
            failures.append(str(p))
    for k in VIP_PILARES_MODULOS:
        if k not in modulos:
            failures.append(f"modulo_falta:{k}")
    ok = len(failures) == 0
    return {
        "objetivos_vip_total": VIP_LOI_EXPECTED + len(VIP_PILARES_MODULOS),
        "loi_md_rastreados": len(loi),
        "pilares_modulos_ok": sum(1 for k in VIP_PILARES_MODULOS if k in modulos),
        "todos_rastreados": ok,
        "fallos": failures,
        "loi_paths": loi_rel,
    }


def merge_vault() -> None:
    if not VAULT_PATH.is_file():
        log("Aviso: no hay master_omega_vault.json; se omite fusión del vault.")
        return
    data = json.loads(VAULT_PATH.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})
    meta["last_sync"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta.setdefault("status", "PRODUCTION_READY_MAYO_2026")
    meta["version"] = RELEASE
    make_url = bool(os.environ.get("MAKE_WEBHOOK_URL", "").strip())
    data["loi_guy_moquet"] = {
        "sello_definitivo_utc": meta["last_sync"],
        "archivos_paris17": list_loi_paris17(),
        "jules_estado": "SELLO_DEFINITIVO_V10",
        "nota": "LOI indexadas; patente y SIRET en identidad del vault.",
    }
    omega_auto = {
        "last_run_utc": meta["last_sync"],
        "release": RELEASE,
        "bunker": "Guy Moquet, París (núcleo operativo)",
        "mesa_redonda": ["Listos", "Gemini", "Copilot", "Manus", "AGENTE70", "Jules"],
        "loi_paris17_md": list_loi_paris17(),
        "make_webhook_configurado": make_url,
        "elevenlabs_configurada": bool(os.environ.get("ELEVENLABS_API_KEY", "").strip()),
        "telegram_configurado": bool(get_telegram_bot_token() and get_telegram_chat_id()),
    }
    omega_auto["vip_watchdog"] = _vip_watchdog_report(data)
    data["cursor_omega_auto"] = omega_auto
    VAULT_PATH.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"Vault fusionado: {VAULT_PATH.resolve()}")
    wd = omega_auto["vip_watchdog"]
    if wd["todos_rastreados"]:
        log(
            "Watchdog VIP: 14/14 objetivos rastreados "
            "(10 LOI + 4 pilares modulos_activos)."
        )
    else:
        log(f"Watchdog VIP: incidencias — {wd['fallos']}")
    log(
        "LOI Guy Moquet / Paris 17: referencias indexadas en cursor_omega_auto "
        "(SIRET 94361019600017 en identidad del vault; sin volcar claves)."
    )


def pin_google_auth_230(req: Path) -> None:
    if not req.is_file():
        return
    lines = req.read_text(encoding="utf-8").splitlines()
    changed = False
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("google-auth==") or s.startswith("google-auth =="):
            out.append("google-auth==2.30.0")
            changed = True
        else:
            out.append(line)
    if changed:
        req.write_text("\n".join(out) + "\n", encoding="utf-8")
        log(f"google-auth fijado a 2.30.0 en {req.relative_to(ROOT)}")


def patch_requirements_google_auth() -> None:
    for rel in (
        "requirements.txt",
        "backend/requirements.txt",
        "voice_agent/requirements.txt",
        "tryonme-voice-agent/requirements.txt",
        "api/requirements.txt",
    ):
        pin_google_auth_230(ROOT / rel)


def verify_make_webhook() -> bool:
    """Valida MAKE_WEBHOOK_URL. Ping POST opcional (OMEGA_MAKE_PING=1) para no disparar el escenario sin querer."""
    url = os.environ.get("MAKE_WEBHOOK_URL", "").strip()
    if not url:
        log("Make: MAKE_WEBHOOK_URL vacío — 404 en puente hasta exportes la URL real (hook.eu2.make.com/…).")
        return False
    if not url.startswith("https://"):
        log("Make: la URL debería ser https:// — revisa el escenario en Make.")
        return False
    if os.environ.get("OMEGA_MAKE_PING", "").strip() != "1":
        log(
            "Make: URL configurada; sin ping HTTP (evita ejecuciones fantasma). "
            "Prueba: OMEGA_MAKE_PING=1 o python3 shopify_make_bridge.py"
        )
        return True
    try:
        r = requests.post(
            url,
            json={"event": "CURSOR_OMEGA_PING", "patente": PATENT, "protocolo": "V10_OMEGA"},
            headers={"Content-Type": "application/json"},
            timeout=25,
        )
    except requests.RequestException as e:
        log(f"Make: error de red — {e}")
        return False
    if r.status_code == 404:
        log("Make: HTTP 404 — URL incorrecta o escenario despublicado; copia el webhook de Make otra vez.")
        return False
    if r.status_code != 200:
        log(f"Make: HTTP {r.status_code} — {r.text[:200]}")
        return False
    log("Make: ping devolvió 200.")
    return True


def sync_colaboradores_via_make() -> tuple[int, int]:
    """Sube JSON de assets/colaboradores/*.json a Make → Shopify (mismo contrato que ShopifyMakeBridge)."""
    from shopify_make_bridge import ShopifyMakeBridge

    d = Path(os.environ.get("COLABORADORES_DIR", str(COLAB_DIR)))
    if not d.is_dir():
        d.mkdir(parents=True, exist_ok=True)
        log(f"Colaboradores: carpeta creada {d.relative_to(ROOT)} (añade .json y re-ejecuta).")
        return 0, 0
    bridge = ShopifyMakeBridge()
    if not bridge.webhook_url:
        log("Colaboradores: sin MAKE_WEBHOOK_URL — no se sube nada a Make.")
        return 0, 0
    ok_n = fail_n = 0
    for fp in sorted(d.glob("*.json")):
        try:
            payload = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            log(f"Colaboradores: omitido {fp.name} — {e}")
            fail_n += 1
            continue
        if not isinstance(payload, dict):
            fail_n += 1
            continue
        if bridge.sync_colaborador(payload):
            ok_n += 1
        else:
            fail_n += 1
    log(f"Colaboradores Make: {ok_n} OK, {fail_n} fallos.")
    return ok_n, fail_n


def bunker_cleanup_activators() -> None:
    """Elimina *activator.py residuales fuera de node_modules/.venv."""
    skip = {".venv", "node_modules", ".git"}
    removed = 0
    for pattern in ("*_activator.py",):
        for p in ROOT.rglob(pattern):
            if not p.is_file() or any(x in p.parts for x in skip):
                continue
            try:
                p.unlink()
                log(f"Limpieza: eliminado {p.relative_to(ROOT)}")
                removed += 1
            except OSError as e:
                log(f"Limpieza: no se pudo borrar {p}: {e}")
    if removed == 0:
        log("Limpieza: no hay *activator.py residuales.")


def synthesize_lily() -> bool:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        log("Sin ELEVENLABS_API_KEY: se omite audio Lily.")
        return False
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES['lily']}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": (
            "Rubén, el búnker de París está sellado. El código es perfecto et la réalité est géographique. J'adore."
        ),
        "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        "voice_settings": V10_VOICE,
    }
    STATIC_AUDIO.parent.mkdir(parents=True, exist_ok=True)
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    if not r.ok:
        log(f"ElevenLabs HTTP {r.status_code}: {r.text[:500]}")
        return False
    STATIC_AUDIO.write_bytes(r.content)
    log(f"Audio Lily OK -> {STATIC_AUDIO.resolve()} ({len(r.content)} bytes)")
    return True


def synthesize_momento_jadore() -> bool:
    """Clip dedicado «Momento J'adore» — Lily, Stability 0.85 (bloque V10_VOICE)."""
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        log("Sin ELEVENLABS_API_KEY: se omite Momento J'adore.")
        return False
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES['lily']}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": (
            "Moment J'adore. La realité est géographique. "
            "Guy Moquet, Stirpe Lafayette, certeza absoluta. Rubén, c'est parfait."
        ),
        "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        "voice_settings": V10_VOICE,
    }
    STATIC_JADORE.parent.mkdir(parents=True, exist_ok=True)
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
    if not r.ok:
        log(f"ElevenLabs J'adore HTTP {r.status_code}: {r.text[:500]}")
        return False
    STATIC_JADORE.write_bytes(r.content)
    log(f"Momento J'adore OK -> {STATIC_JADORE.resolve()} ({len(r.content)} bytes)")
    return True


def telegram_notify(text: str) -> bool:
    token = get_telegram_bot_token()
    chat = get_telegram_chat_id()
    if not token or not chat:
        log("Sin TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) o TELEGRAM_CHAT_ID: se omite Telegram.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": chat, "text": text[:4000]},
        timeout=30,
    )
    if not r.ok:
        log(f"Telegram HTTP {r.status_code}: {r.text[:300]}")
        return False
    log("Telegram: mensaje enviado.")
    return True


def git_commit_and_push() -> int:
    msg = (
        f"OMEGA AUTO: bunker Paris {RELEASE}. {PROTOCOL_PHRASE}. "
        f"{STAMP_C} {STAMP_L} {PATENT}"
    )
    for s in (STAMP_C, STAMP_L, PATENT, PROTOCOL_PHRASE):
        if s not in msg:
            log(f"Error interno: falta texto obligatorio en commit: {s}")
            return 1

    _git("add", "-A")
    st = _git("diff", "--cached", "--quiet", check=False)
    if st.returncode == 0:
        log("Sin cambios en el índice tras git add.")
        did_commit = False
    else:
        _git("commit", "-m", msg)
        log("Commit creado.")
        did_commit = True

    force_push = _force_push_env()
    upstream = _git("rev-parse", "--verify", "@{u}", check=False)
    has_upstream = upstream.returncode == 0

    if not force_push and not has_upstream:
        if did_commit:
            log(
                "Commit local sin push: no hay upstream (@{u}). "
                "Configura tracking o exporta CURSOR_OMEGA_GIT_PUSH_FORCE=1."
            )
        else:
            log("Sin push: sin upstream.")
        return 0 if not did_commit else 2

    # Con push normal, solo tiene sentido empujar si HEAD va por delante del upstream.
    # Aplica tanto si acabamos de hacer commit como si ya había commits locales sin publicar.
    if not force_push:
        ahead_cp = _git("rev-list", "--count", "@{u}..HEAD", check=False)
        try:
            ahead = int((ahead_cp.stdout or "0").strip() or "0")
        except ValueError:
            ahead = 0
        if ahead <= 0:
            log("Sin push: la rama no va por delante del remoto.")
            return 0

    if force_push:
        br = _git("rev-parse", "--abbrev-ref", "HEAD")
        branch = (br.stdout or "").strip()
        if not branch or branch == "HEAD":
            print("Sin push forzado: HEAD detached o rama sin nombre.", file=sys.stderr)
            return 1
        log(f"Push force-with-lease -> origin {branch}")
        _git("push", "--force-with-lease", "origin", branch)
    else:
        _git("push")
    log("Push completado.")
    return 0


def run_omega_pipeline() -> int:
    verify_make_webhook()
    merge_vault()
    patch_requirements_google_auth()
    audio_ok = synthesize_lily()
    jadore_ok = synthesize_momento_jadore()
    sync_colaboradores_via_make()
    bunker_cleanup_activators()

    summary = (
        f"OMEGA AUTO {RELEASE} OK.\n"
        f"Vault + LOI Guy Moquet selladas en JSON.\n"
        f"Audio bunker: {'sí' if audio_ok else 'omitido'}; J'adore: {'sí' if jadore_ok else 'omitido'}\n"
        f"Make: MAKE_WEBHOOK_URL en entorno (sin URL fija en código).\n"
        f"{PROTOCOL_PHRASE} {STAMP_C} {STAMP_L} {PATENT}"
    )
    telegram_notify(summary)

    code = git_commit_and_push()
    if code != 0:
        log(f"Git terminó con código {code}. Revisa upstream / FORCE.")
    return code


def ejecutar_todo() -> int:
    log("Inicio orquestación — Certeza Absoluta / Stirpe Lafayette.")
    return run_omega_pipeline()


class CursorOmegaTotal:
    """
    Fachada con el nombre del protocolo Stirpe Lafayette. Sin secretos en ``self.config``:
    las claves solo se leen de ``os.environ`` dentro de ``synthesize_lily`` / ``telegram_notify``.
    """

    def __init__(self) -> None:
        self.voices = dict(VOICES)
        self.config = {
            "founder": "Rubén Espinar Rodríguez",
            "siret": "94361019600017",
            "patent": PATENT,
            "version": RELEASE,
            "location": "Bunker Guy Moquet, Paris",
        }

    def log(self, msg: str) -> None:
        print(f"[OMEGA-SYSTEM] {msg}")

    def ejecutar_todo(self) -> int:
        self.log("Iniciando baño de oro líquido. La Mesa Redonda toma el mando.")
        return run_omega_pipeline()


def main() -> int:
    try:
        return ejecutar_todo()
    except subprocess.CalledProcessError as e:
        err = (e.stderr or e.stdout or "").strip()
        print(e.returncode, err[:2000], file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Red: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
Orquestador asincrono V11 — limpieza acotada, estado Pau, build Vite.

NO hace: git add ., git push, rm -rf node_modules, ni borra .env.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""
from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE_NAME = "PAU_V11_ORCHESTRA_STATE.json"


async def _run(cmd: list[str], *, cwd: Path) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out_b = await proc.communicate()
    text = (out_b[0] or b"").decode("utf-8", errors="replace").strip()
    return proc.returncode or 0, text


def _safe_rm_dirs(names: tuple[str, ...]) -> None:
    for name in names:
        p = ROOT / name
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            print(f"[OK] Eliminado directorio: {name}")


async def limpieza_acotada() -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: _safe_rm_dirs(
            (".cache", "dist", "out", "build", ".turbo", ".parcel-cache")
        ),
    )
    vite_cache = ROOT / "node_modules" / ".vite"
    if vite_cache.is_dir():
        await loop.run_in_executor(
            None, lambda: shutil.rmtree(vite_cache, ignore_errors=True)
        )
        print("[OK] node_modules/.vite limpiado")


async def escribir_estado_pau() -> None:
    pau_config = {
        "avatar": "Pau_V11_RealTime",
        "engine": "Kalidokit_MediaPipe",
        "status": "DIVINEO_TOTAL",
        "frontend_component": "src/components/RealTimeAvatar.tsx",
        "glb_default": "/assets/models/pau_v11_high_poly.glb",
    }
    path = ROOT / STATE_NAME
    path.write_text(
        json.dumps(pau_config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] Estado Pau -> {path.name}")


async def git_status_breve() -> None:
    code, out = await _run(["git", "status", "-sb"], cwd=ROOT)
    if code == 0 and out:
        print("[GIT]", out.split("\n")[0])
    elif code != 0:
        print("[GIT] (aviso) git status no disponible")


async def npm_build() -> bool:
    print("[*] npm run build...")
    code, out = await _run(["npm", "run", "build"], cwd=ROOT)
    if out:
        tail = out[-4000:] if len(out) > 4000 else out
        print(tail)
    if code != 0:
        print("[ERROR] Build fallo.")
        return False
    print("[OK] Build completado.")
    return True


async def main() -> int:
    print("--- Protocolo purga V11 (async) ---")
    await asyncio.gather(limpieza_acotada(), escribir_estado_pau(), git_status_breve())
    ok = await npm_build()
    print("Listo. Push manual si aplica; nunca git add . con .env.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

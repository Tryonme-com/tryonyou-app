#!/usr/bin/env python3
"""
Restauración nodo Marais (75004) + claves Firebase para el applet.
No sobrescribe .env entero: fusiona claves VITE_* para no perder el resto del bunker.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from firebase_reprovision_guard import exit_if_firebase_applet_locked

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "firebase-applet-config.json"
ENV_PATH = ROOT / ".env"

# Valores solicitados para gen-lang-client-0066102635 (Marais / Lafayette)
# Nota: si Firebase devuelve auth/invalid-api-key, sustituye apiKey por la clave Web real
# en Firebase Console → Configuración del proyecto → Tus apps → SDK.
FIREBASE_CONFIG = {
    "_manifest": "Reprovisión Marais — apiKey real vía Consola o .env (VITE_FIREBASE_API_KEY).",
    "apiKey": "",
    "authDomain": "gen-lang-client-0066102635.firebaseapp.com",
    "projectId": "gen-lang-client-0066102635",
    "storageBucket": "gen-lang-client-0066102635.appspot.com",
    "messagingSenderId": "8800075004",
    "appId": "1:8800075004:web:marais-soberano",
    "measurementId": "",
}

# Debe coincidir con src/lib/firebaseApplet.ts (VITE_FIREBASE_API_KEY, no VITE_FIREBASE_KEY)
ENV_LINES = {
    "VITE_FIREBASE_API_KEY": FIREBASE_CONFIG["apiKey"],
    "VITE_FIREBASE_MESSAGING_SENDER_ID": FIREBASE_CONFIG["messagingSenderId"],
    "VITE_FIREBASE_APP_ID": FIREBASE_CONFIG["appId"],
    "VITE_DISTRICT": "75004",
    "VITE_CONTRACT_VALUE": "88000",
}


def _merge_env(path: Path, updates: dict[str, str]) -> None:
    """Sustituye claves existentes o añade al final; no borra el resto del .env."""
    lines: list[str] = []
    if path.is_file():
        lines = path.read_text(encoding="utf-8").splitlines()
    keys_done: set[str] = set()
    out: list[str] = []
    for line in lines:
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
        if m and m.group(1) in updates:
            key = m.group(1)
            out.append(f"{key}={updates[key]}")
            keys_done.add(key)
        else:
            out.append(line)
    for key, val in updates.items():
        if key not in keys_done:
            out.append(f"{key}={val}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def restore_sovereignty_keys() -> None:
    exit_if_firebase_applet_locked("fix_marais.py")
    CONFIG_PATH.write_text(
        json.dumps(FIREBASE_CONFIG, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    _merge_env(ENV_PATH, ENV_LINES)

    print("✅ [JULES]: firebase-applet-config.json actualizado.")
    print("✅ [MARCEL]: .env fusionado (VITE_FIREBASE_API_KEY + nodo 75004 + contrato 88k).")
    print(
        "⚠️  Si sigue auth/invalid-api-key: pega la apiKey real desde Firebase Console "
        "(Web app) y vuelve a ejecutar este script o edita .env a mano."
    )
    print("🚀 SISTEMA READY.")


if __name__ == "__main__":
    restore_sovereignty_keys()

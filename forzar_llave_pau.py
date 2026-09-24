#!/usr/bin/env python3
"""Escribe firebase-applet-config.json para el proyecto gen-lang-client-0066102635."""
import json
from pathlib import Path

from firebase_reprovision_guard import exit_if_firebase_applet_locked

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "firebase-applet-config.json"


def forzar_llave_pau() -> None:
    exit_if_firebase_applet_locked("forzar_llave_pau.py")
    pau_config = {
        "_manifest": "Reprovisión explícita — misma estructura que firebase-applet-config.json sellado.",
        "apiKey": "",
        "authDomain": "gen-lang-client-0066102635.firebaseapp.com",
        "projectId": "gen-lang-client-0066102635",
        "storageBucket": "gen-lang-client-0066102635.appspot.com",
        "messagingSenderId": "8800075004",
        "appId": "1:8800075004:web:diamond",
        "measurementId": "",
    }
    CONFIG.write_text(json.dumps(pau_config, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
    print("✅ Llave Firebase RESTAURADA (firebase-applet-config.json).")
    print("✅ Nodo Haussmann (75009) / Marais (75004) — mismo proyecto.")
    print("🚀 P.A.U. / DIAMANTE: si persiste auth/invalid-api-key, copia apiKey desde Firebase Console → Web app, o define VITE_FIREBASE_API_KEY en .env.")
    print("🚀 P.A.U. OPERATIVO: ¡BOOM!")


if __name__ == "__main__":
    forzar_llave_pau()

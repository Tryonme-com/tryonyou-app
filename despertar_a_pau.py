#!/usr/bin/env python3
"""
Despertar P.A.U. — escribe firebase-applet-config.json válido (proyecto gen-lang-client-0066102635).

No inyecta JS en App.tsx/main.tsx (rompería TypeScript): el bypass soberano vive en App.tsx
(forceUserCheckIfPilotCold + initPauAlpha). No uses apiKey ficticia tipo BYPASS_DIAMANTE.

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
from pathlib import Path

from firebase_reprovision_guard import exit_if_firebase_applet_locked

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "firebase-applet-config.json"

PAU_CONFIG = {
    "_manifest": (
        "Reprovisión explícita (TRYONYOU_FIREBASE_REPROVISION=1). "
        "Pega apiKey Web real o usa VITE_FIREBASE_API_KEY. PCT/EP2025/067317."
    ),
    "apiKey": "",
    "authDomain": "gen-lang-client-0066102635.firebaseapp.com",
    "projectId": "gen-lang-client-0066102635",
    "storageBucket": "gen-lang-client-0066102635.appspot.com",
    "messagingSenderId": "8800075004",
    "appId": "1:8800075004:web:diamond",
    "measurementId": "",
}


def despertar_a_pau() -> None:
    exit_if_firebase_applet_locked("despertar_a_pau.py")
    CONFIG.write_text(
        json.dumps(PAU_CONFIG, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("✅ firebase-applet-config.json restaurado (SDK Web completo).")
    print("✅ Nodos Lafayette 75009 + BHV Marais 75004: lógica en src/App.tsx (UserCheck + initPauAlpha).")
    print("⚠️  Si auth/invalid-api-key: pega apiKey real desde Firebase Console o VITE_FIREBASE_API_KEY en .env.")
    print("🚀 P.A.U. — estado DIAMANTE; contrato narrativo 194.800 € en UserCheck.")


if __name__ == "__main__":
    despertar_a_pau()

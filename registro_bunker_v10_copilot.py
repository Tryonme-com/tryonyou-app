"""
Registro TRYONYOU V10 — escritura en hoja de cálculo maestra (Divineo_Leads_DB).

Autenticación híbrida: usa ``credentials.json`` si existe en el directorio de
trabajo; en caso contrario recurre a las credenciales por defecto de Google
Cloud CLI (``gcloud auth application-default login``).

Ejecución::

    python3 registro_bunker_v10_copilot.py

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""
from __future__ import annotations

import datetime
import os
import sys

import gspread
from google.auth import default
from google.oauth2.service_account import Credentials

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_SPREADSHEET_NAME = "Divineo_Leads_DB"

_REGISTRO: dict[str, object] = {
    "Fecha_Registro": "",  # se rellena en tiempo de ejecución
    "Empresa": "TRYONYOU",
    "SIRET": "94361019600017",
    "Contacto_Destino": "Elena Grandini / Julia (Bpifrance) / E. Gandini (Lafayette)",
    "Emails": (
        "elena.grandini@bpifrance.fr, julia.leborgne@bpifrance.fr, "
        "e.gandini@galerieslafayette.com"
    ),
    "Contrato_Referencia": "Le Bon Marché (LVMH)",
    "Monto_Contrato": 100000.00,
    "Vencimiento": "2026-05-09",
    "Patente": "PCT/EP2025/067317",
    "Solicitud_Bourse_FT": 10000.00,
    "Estado": "Pendiente de Envío",
    "Agente_Asignado": "Jules V7 (Copilot)",
}


def _autenticar() -> gspread.Client:
    print("[SISTEMA PEGASO]: Verificando credenciales...")
    if os.path.exists("credentials.json"):
        print("[SISTEMA]: Archivo 'credentials.json' detectado. Usando Service Account...")
        creds: Credentials = Credentials.from_service_account_file(
            "credentials.json", scopes=_SCOPES
        )
    else:
        print(
            "[SISTEMA]: 'credentials.json' no encontrado. "
            "Usando Google Cloud CLI default credentials..."
        )
        creds, _ = default(scopes=_SCOPES)
    return gspread.authorize(creds)


def ejecutar_mision_v10_copilot() -> int:
    print("\n--- INICIANDO EJECUCIÓN: REGISTRO TRYONYOU V10 (MODO LOCAL) ---")
    try:
        gc = _autenticar()
        print("[OK]: Autenticación con la arquitectura centralizada exitosa.")

        registro = dict(_REGISTRO)
        registro["Fecha_Registro"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            sh = gc.open(_SPREADSHEET_NAME)
            worksheet = sh.get_worksheet(0)
            worksheet.append_row(list(registro.values()))
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"\n[ERROR CRÍTICO]: No se encontró '{_SPREADSHEET_NAME}'.")
            print(
                "Tito Paco advierte: Si usas 'credentials.json', asegúrate de compartir "
                "tu Google Sheet con el email del Service Account."
            )
            return 1

        sep = "=" * 60
        print(f"\n{sep}")
        print("VALIDACIÓN DE REGISTRO PARA JULES V7 (DESDE COPILOT)")
        print(sep)
        for campo, valor in registro.items():
            print(f"  {campo}: {valor}")
        print("\n[ÉXITO]: Datos inyectados en la base de datos maestra.")
        print("[ESTADO]: Jules V7 activado. Esperando despliegue de correos comerciales.")
        print(sep)
        return 0

    except Exception as exc:
        print(f"\n[ERROR MÓDULO PEGASO]: {exc}")
        print(
            "Sugerencia Técnica: Asegúrate de estar validado en tu terminal local "
            "ejecutando `gcloud auth application-default login` o de incluir un "
            "`credentials.json` en esa misma carpeta."
        )
        return 1


def main() -> int:
    return ejecutar_mision_v10_copilot()


if __name__ == "__main__":
    raise SystemExit(main())

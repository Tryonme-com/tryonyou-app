"""
Registro Búnker V10 – Jules (Copilot/IDE local)
================================================
Autentica con la API de Google Sheets mediante Service Account
(credentials.json) o Application Default Credentials y escribe
una fila de registro estratégico en 'Divineo_Leads_DB'.

Dependencias adicionales requeridas:
    pip install gspread>=6.0 google-auth>=1.12.0
"""

from __future__ import annotations

import datetime
import os

try:
    import gspread
    from google.auth import default
    from google.oauth2.service_account import Credentials
except ImportError as exc:
    raise SystemExit(
        "[ERROR]: Dependencias no encontradas. "
        "Ejecuta: pip install gspread>=6.0 google-auth>=1.12.0"
    ) from exc

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
_SPREADSHEET_NAME = "Divineo_Leads_DB"


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
def _authenticate() -> gspread.Client:
    if os.path.exists("credentials.json"):
        print("[SISTEMA]: Archivo 'credentials.json' detectado. Inicializando Service Account...")
        creds = Credentials.from_service_account_file("credentials.json", scopes=_SCOPES)
    else:
        print(
            "[SISTEMA]: 'credentials.json' no encontrado. "
            "Intentando usar Google Cloud CLI default credentials..."
        )
        creds, _ = default(scopes=_SCOPES)

    gc = gspread.authorize(creds)
    print("[OK]: Autenticación con la arquitectura centralizada exitosa.")
    return gc


# ---------------------------------------------------------------------------
# Registro principal
# ---------------------------------------------------------------------------
def ejecutar_mision_v10_copilot() -> int:
    print("\n--- INICIANDO EJECUCIÓN: REGISTRO TRYONYOU V10 (MODO LOCAL) ---")

    try:
        gc = _authenticate()
    except Exception as exc:
        print(f"\n[ERROR MÓDULO PEGASO]: {exc}")
        print(
            "Sugerencia Técnica: Asegúrate de estar validado en tu terminal local "
            "ejecutando `gcloud auth application-default login` "
            "o de incluir un `credentials.json` en esa misma carpeta."
        )
        return 1

    hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_for_sheet: dict[str, object] = {
        "Fecha_Registro": hoy,
        "Empresa": "TRYONYOU",
        "SIRET": "94361019600017",
        "Contacto_Destino": "Elena Grandini / Julia (Bpifrance) / E. Gandini (Lafayette)",
        "Emails": (
            "elena.grandini@bpifrance.fr, "
            "julia.leborgne@bpifrance.fr, "
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

    try:
        sh = gc.open(_SPREADSHEET_NAME)
        worksheet = sh.get_worksheet(0)
        worksheet.append_row(list(data_for_sheet.values()))

        sep = "=" * 60
        print(f"\n{sep}")
        print("VALIDACIÓN DE REGISTRO PARA JULES V7 (DESDE COPILOT)")
        print(sep)
        for key, value in data_for_sheet.items():
            print(f"  {key}: {value}")
        print("\n[ÉXITO]: Datos inyectados en la base de datos maestra.")
        print("[ESTADO]: Jules V7 activado. Esperando despliegue de correos comerciales.")
        print(sep)
        return 0

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\n[ERROR CRÍTICO]: No se encontró '{_SPREADSHEET_NAME}'.")
        print(
            "Tito Paco advierte: Si usas 'credentials.json', asegúrate de compartir "
            "tu Google Sheet con el email del Service Account."
        )
        return 1

    except Exception as exc:
        print(f"\n[ERROR MÓDULO PEGASO]: {exc}")
        return 1


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def main() -> int:
    return ejecutar_mision_v10_copilot()


if __name__ == "__main__":
    raise SystemExit(main())

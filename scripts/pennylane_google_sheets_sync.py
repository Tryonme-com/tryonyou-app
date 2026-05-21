from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import gspread
import requests
from google.oauth2.service_account import Credentials
from gspread.utils import rowcol_to_a1

PENNYLANE_API_URL = "https://api.pennylane.com/v1"
PENNYLANE_API_KEY = os.environ.get("PENNYLANE_API_KEY", "").strip()
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "").strip()
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
REQUEST_TIMEOUT_SECONDS = 30
VAT_RATE_STANDARD = Decimal("0.20")
LOG_PREFIX = "[PennylaneSync]"

EXPECTED_HEADERS = [
    "ID Transacción",
    "Fecha",
    "Concepto",
    "Importe Total",
    "Base Imponible",
    "Cuota IVA/TVA",
    "Estado",
    "Sincronizado En",
]


def _require_env(name: str, value: str) -> str:
    if value:
        return value
    raise ValueError(f"Falta variable de entorno requerida: {name}")


def get_google_sheet_client() -> gspread.Client:
    """Autentica con la cuenta de servicio de Google."""
    service_account_raw = _require_env("GOOGLE_SERVICE_ACCOUNT_JSON", GOOGLE_SERVICE_ACCOUNT_JSON)
    try:
        service_account_info = json.loads(service_account_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON no contiene un JSON válido") from exc

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
    return gspread.authorize(credentials)


def fetch_pennylane_transactions() -> list[dict[str, Any]]:
    """Extrae transacciones bancarias recientes desde Pennylane."""
    api_key = _require_env("PENNYLANE_API_KEY", PENNYLANE_API_KEY)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    endpoint = f"{PENNYLANE_API_URL}/bank_transactions"

    response = requests.get(endpoint, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
    if response.status_code != 200:
        raise RuntimeError(f"Error Pennylane ({response.status_code}): {response.text}")

    payload = response.json()
    if isinstance(payload, dict):
        transactions = payload.get("bank_transactions", [])
        if isinstance(transactions, list):
            return [tx for tx in transactions if isinstance(tx, dict)]
        return []
    if isinstance(payload, list):
        return [tx for tx in payload if isinstance(tx, dict)]
    return []


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value or "0"))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _extract_vat_from_total(amount_with_vat: Decimal, tva_rate: Decimal) -> Decimal:
    if amount_with_vat > 0 or tva_rate <= 0:
        # Business default: only expense transactions (negative amounts)
        # get reverse VAT extraction in this automation flow.
        return Decimal("0")
    # Reverse VAT extraction from VAT-inclusive amount:
    # total * (rate / (1 + rate)) -> VAT component
    return (amount_with_vat * (tva_rate / (Decimal("1") + tva_rate))).quantize(Decimal("0.01"))


def process_and_format_data(transactions: list[dict[str, Any]]) -> list[list[Any]]:
    """Filtra, calcula tasas y formatea filas para la hoja de cálculo."""
    formatted_rows: list[list[Any]] = []
    synced_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for tx in transactions:
        tx_id = tx.get("id")
        if tx_id is None:
            continue

        amount = _to_decimal(tx.get("amount"))
        is_expense = amount < 0
        # Business default from statement: 20% VAT for expenses, exempt otherwise.
        # Reduced/special VAT rates are intentionally out of scope for this sync.
        tva_rate = VAT_RATE_STANDARD if is_expense else Decimal("0")
        vat_amount = _extract_vat_from_total(amount, tva_rate)
        base_imponible = (amount - vat_amount).quantize(Decimal("0.01"))

        matched = bool(tx.get("matched") or tx.get("matched_invoice"))
        status = "Conciliado" if matched else "Pendiente Justificante"

        row = [
            str(tx_id),
            str(tx.get("date", "")),
            str(tx.get("label", "Sin concepto")),
            float(amount),
            float(base_imponible),
            float(vat_amount),
            status,
            synced_at,
        ]
        formatted_rows.append(row)

    return formatted_rows


def _ensure_headers(sheet: gspread.Worksheet) -> None:
    first_row = sheet.row_values(1)
    if not first_row:
        end_cell = rowcol_to_a1(1, len(EXPECTED_HEADERS))
        sheet.update(f"A1:{end_cell}", [EXPECTED_HEADERS], value_input_option="USER_ENTERED")
        return

    if len(first_row) < len(EXPECTED_HEADERS):
        raise RuntimeError(
            f"La hoja contiene {len(first_row)} columnas en la fila 1 y se esperaban al menos {len(EXPECTED_HEADERS)}."
        )

    # Additional columns are allowed; we validate only the managed A:H structure.
    normalized_existing = [cell.strip() for cell in first_row[: len(EXPECTED_HEADERS)]]
    if normalized_existing != EXPECTED_HEADERS:
        raise RuntimeError(
            "La fila 1 de la hoja no coincide con la estructura esperada: "
            + ", ".join(EXPECTED_HEADERS)
        )


def sync_to_google_sheets(rows: list[list[Any]]) -> int:
    """Sube datos limpios evitando duplicados por ID de transacción."""
    spreadsheet_id = _require_env("SPREADSHEET_ID", SPREADSHEET_ID)
    client = get_google_sheet_client()
    sheet = client.open_by_key(spreadsheet_id).sheet1

    _ensure_headers(sheet)
    existing_ids = {value.strip() for value in sheet.col_values(1)[1:] if value.strip()}
    new_rows: list[list[Any]] = []
    for row in rows:
        if not row:
            continue
        row_id = str(row[0]).strip()
        if not row_id or row_id in existing_ids:
            continue
        new_rows.append(row)

    if not new_rows:
        print(f"{LOG_PREFIX} No hay transacciones nuevas para añadir. Todo al día.")
        return 0

    sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"{LOG_PREFIX} Sincronizadas con éxito {len(new_rows)} nuevas transacciones.")
    return len(new_rows)


def main_execution() -> int:
    """Ejecutor principal del flujo contable."""
    try:
        print(f"{LOG_PREFIX} Iniciando extracción de datos financieros de Pennylane...")
        raw_transactions = fetch_pennylane_transactions()
        print(f"{LOG_PREFIX} Transacciones recibidas: {len(raw_transactions)}")

        print(f"{LOG_PREFIX} Procesando importes, desgloses de TVA y estados de conciliación...")
        processed_data = process_and_format_data(raw_transactions)

        print(f"{LOG_PREFIX} Escribiendo datos en Google Sheets...")
        sync_to_google_sheets(processed_data)
        return 0
    except Exception as exc:
        print(f"{LOG_PREFIX} ERROR: Fallo en la ejecución automática: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main_execution())

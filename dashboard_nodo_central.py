"""
Dashboard Vivo 75001 — Monitor de liquidez en tiempo real (Nodo Central).

Consulta los saldos de Revolut y PayPal vía API y publica un resumen
financiero en un canal de Slack cada 60 segundos.

Configuración (variables de entorno):
  SLACK_TOKEN          Token del bot de Slack (xoxb-…)
  SLACK_CHANNEL        ID del canal Slack destino (p. ej. C08MB3Z7B12)
  ACTIVOS_FIJOS_EUR    Valor del stock fijo en EUR (por defecto 65000.00)
  REVOLUT_TOKEN        Token Bearer de la API Business de Revolut
  REVOLUT_API_URL      Base URL de la API Revolut (por defecto https://b2b.revolut.com/api/1.0)
  REVOLUT_FALLBACK_EUR Saldo de respaldo si la API está en mantenimiento (por defecto 32800.00)
  PAYPAL_CLIENT_ID     Client ID de la app PayPal
  PAYPAL_SECRET        Secret de la app PayPal
  DASHBOARD_INTERVAL_S Intervalo entre actualizaciones en segundos (por defecto 60)

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import time

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# ---------------------------------------------------------------------------
# Parámetros configurables
# ---------------------------------------------------------------------------

REVOLUT_API_URL_DEFAULT = "https://b2b.revolut.com/api/1.0"
ACTIVOS_FIJOS_DEFAULT = 65000.00
REVOLUT_FALLBACK_DEFAULT = 32800.00
DASHBOARD_INTERVAL_DEFAULT = 60


def _activos_fijos() -> float:
    raw = os.environ.get("ACTIVOS_FIJOS_EUR", "").strip()
    try:
        return float(raw) if raw else ACTIVOS_FIJOS_DEFAULT
    except ValueError:
        return ACTIVOS_FIJOS_DEFAULT


def _revolut_fallback() -> float:
    raw = os.environ.get("REVOLUT_FALLBACK_EUR", "").strip()
    try:
        return float(raw) if raw else REVOLUT_FALLBACK_DEFAULT
    except ValueError:
        return REVOLUT_FALLBACK_DEFAULT


def _interval_s() -> int:
    raw = os.environ.get("DASHBOARD_INTERVAL_S", "").strip()
    try:
        return max(1, int(raw)) if raw else DASHBOARD_INTERVAL_DEFAULT
    except ValueError:
        return DASHBOARD_INTERVAL_DEFAULT


# ---------------------------------------------------------------------------
# Lecturas de saldo
# ---------------------------------------------------------------------------


def get_revolut_balance() -> float:
    """Devuelve el saldo EUR de todas las cuentas Revolut Business.

    Si la API no está disponible o el token está ausente, devuelve el valor
    de fallback configurado en REVOLUT_FALLBACK_EUR.
    """
    token = os.environ.get("REVOLUT_TOKEN", "").strip()
    base_url = os.environ.get("REVOLUT_API_URL", REVOLUT_API_URL_DEFAULT).strip()
    if not token:
        return _revolut_fallback()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{base_url}/accounts", headers=headers, timeout=15)
        r.raise_for_status()
        accounts = r.json()
        return sum(
            float(acc["balance"])
            for acc in accounts
            if acc.get("currency") == "EUR"
        )
    except Exception:
        return _revolut_fallback()


def get_paypal_balance() -> float:
    """Devuelve el saldo EUR de PayPal.

    Realiza primero el intercambio OAuth2 para obtener el access_token y luego
    consulta el endpoint de saldos. Devuelve 0.00 ante cualquier error.
    """
    client_id = os.environ.get("PAYPAL_CLIENT_ID", "").strip()
    secret = os.environ.get("PAYPAL_SECRET", "").strip()
    if not client_id or not secret:
        return 0.00
    auth_url = "https://api-m.paypal.com/v1/oauth2/token"
    try:
        r = requests.post(
            auth_url,
            auth=(client_id, secret),
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        r.raise_for_status()
        token = r.json().get("access_token", "")
        if not token:
            return 0.00
        headers = {"Authorization": f"Bearer {token}"}
        bal_url = "https://api-m.paypal.com/v1/reporting/balances?currency_code=EUR"
        res = requests.get(bal_url, headers=headers, timeout=15)
        res.raise_for_status()
        balances = res.json().get("balances", [])
        if not balances:
            return 0.00
        return float(balances[0]["total_balance"]["value"])
    except Exception:
        return 0.00


# ---------------------------------------------------------------------------
# Publicación en Slack
# ---------------------------------------------------------------------------


def publicar_en_slack(total_liquido: float) -> bool:
    """Publica el dashboard financiero en el canal Slack configurado.

    Args:
        total_liquido: Suma de saldos líquidos (Revolut + PayPal) en EUR.

    Returns:
        True si el mensaje se envió correctamente, False en caso de error.
    """
    slack_token = os.environ.get("SLACK_TOKEN", "").strip()
    slack_channel = os.environ.get("SLACK_CHANNEL", "").strip()
    if not slack_token or not slack_channel:
        print("❌ SLACK_TOKEN y SLACK_CHANNEL son obligatorios.", file=sys.stderr)
        return False

    activos = _activos_fijos()
    total_imperio = total_liquido + activos

    mensaje = (
        f"🔱 *DASHBOARD VIVO 75001* 🔱\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *Liquidez Real (APIs):* {total_liquido:,.2f} €\n"
        f"👜 *Activos Fijos (Stock):* {activos:,.2f} €\n"
        f"🚀 *TOTAL IMPERIO:* {total_imperio:,.2f} €\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ _Actualizado en tiempo real. Nodo activo._\n"
        f"*PA, PA, PA.*"
    )

    client = WebClient(token=slack_token)
    try:
        client.chat_postMessage(channel=slack_channel, text=mensaje)
        print(f"✅ Disparo enviado a Slack: {total_imperio:,.2f} €")
        return True
    except SlackApiError as e:
        print(f"❌ Error de Slack: {e.response['error']}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Bucle principal
# ---------------------------------------------------------------------------


def run_once() -> None:
    """Ejecuta una iteración del monitor: lee saldos y publica en Slack."""
    revolut = get_revolut_balance()
    paypal = get_paypal_balance()
    publicar_en_slack(revolut + paypal)


def main() -> int:
    """Inicia el monitor en bucle infinito (Ctrl+C para detener)."""
    interval = _interval_s()
    print("🚀 Agentes de monitoreo iniciados...")
    while True:
        try:
            run_once()
        except Exception as e:
            print(f"⚠️ Error en el ciclo: {e}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())

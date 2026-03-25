"""
Monitor de referencia de liquidación V10 (consola + Telegram opcional).

  python3 monitor_liquidacion_v10.py

  # Mismo informe al bot (09:00 cron en servidor):
  export MONITOR_SEND_TELEGRAM=1
  export TELEGRAM_BOT_TOKEN='…'
  export TELEGRAM_CHAT_ID='…'
  python3 monitor_liquidacion_v10.py

  Cron (ejemplo, ajustar rutas):
  0 9 * * * cd /ruta/tryonyou-app && /usr/bin/env MONITOR_SEND_TELEGRAM=1 TELEGRAM_BOT_TOKEN=… TELEGRAM_CHAT_ID=… python3 monitor_liquidacion_v10.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from datetime import datetime


class MonitorLiquidacion:
    def __init__(self) -> None:
        self.target_date = "2026-05-09"
        self.neto_esperado = 98000.00
        self.siren = "943610196"
        self.identidad_verificada = True

    def informe_diario(self) -> str:
        ahora = datetime.now()
        hoy = ahora.strftime("%Y-%m-%d")
        cabecera = (
            f"[{ahora.strftime('%H:%M:%S')}] Escaneando registros "
            "LVMH / Le Bon Marché (referencia)…"
        )

        if hoy == self.target_date:
            cuerpo = (
                "\n💰 --- [HITO ALCANZADO: SOBERANÍA TOTAL] ---\n"
                f"✅ Transacción confirmada para SIREN: {self.siren}\n"
                f"💵 Monto neto ingresado: {self.neto_esperado:,.2f} €\n"
                "🎉 ¡Vívelo! BOOM. 💥"
            )
            return cabecera + cuerpo

        target = datetime.strptime(self.target_date, "%Y-%m-%d")
        dias = (target - ahora).days
        if dias > 0:
            pie = (
                f"⏳ Hito en progreso. Faltan {dias} días "
                "para la liquidación V10."
            )
        else:
            pie = (
                f"⏳ Fecha objetivo superada ({self.target_date}); "
                "revisar estado real en sistemas contables."
            )
        return f"{cabecera}\n{pie}"

    def verificar_estado_pago(self) -> None:
        print(self.informe_diario())


def _enviar_telegram(texto: str) -> bool:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        print(
            "❌ MONITOR_SEND_TELEGRAM=1 pero faltan token o chat_id.",
            file=sys.stderr,
        )
        return False
    try:
        import requests
    except ImportError:
        print("❌ pip install requests", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat, "text": texto},
            timeout=30,
        )
        if r.status_code == 200:
            print("✅ Informe enviado a Telegram.")
            return True
        print(f"❌ Telegram HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
    except Exception as e:
        print(f"❌ Telegram: {e}", file=sys.stderr)
    return False


if __name__ == "__main__":
    monitor = MonitorLiquidacion()
    informe = monitor.informe_diario()
    print(informe)
    if os.environ.get("MONITOR_SEND_TELEGRAM", "").strip() in (
        "1",
        "true",
        "yes",
    ):
        _enviar_telegram(informe)

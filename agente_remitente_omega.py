"""
Agente remitente Omega — entrega vía Slack (sin SMTP/Gmail).

- Por defecto solo **simula** (no envía). Envío real: SLACK_WEBHOOK_URL + OMEGA_SEND=1 + OMEGA_SEND_CONFIRM=1.
- Contactos: JSON vía OMEGA_CONTACTOS_JSON (campo \"nombre\"; el email es solo metadato, el aviso va a Slack).

Patente (ref.): PCT/EP2025/067317
SIRET (ref.): 94361019600017

  python3 agente_remitente_omega.py
  OMEGA_SEND=1 OMEGA_SEND_CONFIRM=1 SLACK_WEBHOOK_URL=... python3 agente_remitente_omega.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from divineo_slack import slack_post


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


class AgenteRemitenteOmega:
    def __init__(self) -> None:
        self.founder = "Rubén Espinar Rodríguez"
        self.patent = "PCT/EP2025/067317"
        self.siret = "94361019600017"
        self.monto_solicitado = os.environ.get("OMEGA_MONTO_TEXTO", "10.000€").strip()
        self.project_ref = os.environ.get(
            "OMEGA_PROJECT_REF",
            "gen-lang-client-0091228222",
        ).strip()
        self.contactos = self._cargar_contactos()

    def _cargar_contactos(self) -> list[dict[str, str]]:
        raw_path = os.environ.get("OMEGA_CONTACTOS_JSON", "").strip()
        if raw_path:
            p = Path(raw_path).expanduser()
            if p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return [x for x in data if isinstance(x, dict)]
        return [
            {"nombre": "Gestor Bpifrance", "email": "contacto@bpifrance.fr"},
            {"nombre": "Inversor Estratégico", "email": "partner@tryonme.com"},
        ]

    def redactar_cuerpo(self, nombre_receptor: str) -> str:
        return f"""Estimado/a {nombre_receptor},

Como responsable del proyecto TryOnYou.org, referencia operativa v10 (Slack / interno).

- Patente: {self.patent}
- SIRET: {self.siret}
- Proyecto (ref.): {self.project_ref}
- Importe narrativa piloto: {self.monto_solicitado}

Atentamente,
{self.founder}
"""

    def enviar_masivo(self, *, send: bool) -> int:
        print(
            f"🚀 Protocolo referencia {self.patent} — destinatarios (canal Slack): {len(self.contactos)}"
        )
        if send and not os.environ.get("SLACK_WEBHOOK_URL", "").strip():
            print("❌ Para enviar define SLACK_WEBHOOK_URL.", file=sys.stderr)
            return 2

        for persona in self.contactos:
            nombre = str(persona.get("nombre", "Contacto"))
            email = str(persona.get("email", "")).strip()
            texto = self.redactar_cuerpo(nombre) + (f"\n[meta contacto: {email}]" if email else "")

            if not send:
                print(f"📣 [dry-run] Slack → {nombre}\n---\n{texto[:400]}…")
                continue

            if not slack_post(f"*TryOnYou Omega · {nombre}*\n```\n{texto[:2800]}\n```"):
                print(f"❌ Fallo Slack para {nombre}", file=sys.stderr)
                return 1
            print(f"✅ Slack enviado: {nombre}")

        print(
            "\n--- Operación finalizada (Slack)" if send else "--- Solo simulación ---"
        )
        return 0


if __name__ == "__main__":
    send = _truthy("OMEGA_SEND")
    if send and not _truthy("OMEGA_SEND_CONFIRM"):
        print(
            "Para envío real añade OMEGA_SEND_CONFIRM=1 (evita envíos accidentales).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    raise SystemExit(AgenteRemitenteOmega().enviar_masivo(send=send))

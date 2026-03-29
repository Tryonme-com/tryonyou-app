"""
Agente remitente Omega — borradores de correo multi-destinatario (demo / prueba).

- Por defecto solo **simula** (no envía). Envío real: GMAIL_USER + GMAIL_APP_PASSWORD,
  OMEGA_SEND=1 y OMEGA_SEND_CONFIRM=1.
- Contactos: demo embebida o JSON vía OMEGA_CONTACTOS_JSON.
- **No** ejecuta git. Commit/push manual con el mensaje que exija el equipo.

Patente (ref.): PCT/EP2025/067317
SIRET (ref.): 94361019600017

  python3 agente_remitente_omega.py
  OMEGA_SEND=1 OMEGA_SEND_CONFIRM=1 GMAIL_USER=... GMAIL_APP_PASSWORD=... python3 agente_remitente_omega.py
"""
from __future__ import annotations

import json
import os
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import smtplib


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
        self.from_addr = os.environ.get("GMAIL_USER", "").strip() or os.environ.get(
            "OMEGA_FROM_EMAIL",
            "",
        ).strip()
        self.contactos = self._cargar_contactos()

    def _cargar_contactos(self) -> list[dict[str, str]]:
        raw_path = os.environ.get("OMEGA_CONTACTOS_JSON", "").strip()
        if raw_path:
            p = Path(raw_path).expanduser()
            if p.is_file():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    return [
                        x
                        for x in data
                        if isinstance(x, dict) and str(x.get("email", "")).strip()
                    ]
        return [
            {"nombre": "Gestor Bpifrance", "email": "contacto@bpifrance.fr"},
            {"nombre": "Inversor Estratégico", "email": "partner@tryonme.com"},
        ]

    def redactar_cuerpo(self, nombre_receptor: str) -> str:
        return f"""
Estimado/a {nombre_receptor},

Como responsable del proyecto TryOnYou.org, le trasladamos material de referencia
sobre el protocolo operativo v10 (borrador / comunicación interna).

Detalles de referencia:
- Patente internacional: {self.patent}
- SIRET: {self.siret}
- Identificador de proyecto (referencia): {self.project_ref}

Importe de referencia mencionado en narrativa piloto: {self.monto_solicitado}.

Este correo es generado desde herramienta local; validar siempre datos y destinatarios
antes de uso formal. No sustituye documentación legal ni portales oficiales.

Atentamente,
{self.founder}
"""

    def enviar_masivo(self, *, send: bool) -> int:
        print(
            f"🚀 Protocolo referencia {self.patent} — destinatarios: {len(self.contactos)}"
        )
        if send and not self.from_addr:
            print(
                "❌ Para enviar define GMAIL_USER (u OMEGA_FROM_EMAIL) y GMAIL_APP_PASSWORD.",
                file=sys.stderr,
            )
            return 2

        for persona in self.contactos:
            nombre = str(persona.get("nombre", "Contacto"))
            email = str(persona.get("email", "")).strip()
            if not email:
                print(f"⚠️  Sin email: {persona!r}", file=sys.stderr)
                continue

            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = email
            msg["Subject"] = (
                f"Referencia operativa v10 — {self.patent} — {self.founder.split()[0]}"
            )
            msg.attach(MIMEText(self.redactar_cuerpo(nombre), "plain", "utf-8"))

            if not send:
                print(f"📧 [dry-run] {nombre} <{email}> — asunto listo")
                continue

            app_pw = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
            if not app_pw:
                print("❌ Falta GMAIL_APP_PASSWORD.", file=sys.stderr)
                return 2

            context = ssl.create_default_context()
            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(self.from_addr, app_pw)
                    server.send_message(msg)
                print(f"✅ Enviado: {nombre} ({email})")
            except OSError as e:
                print(f"❌ Fallo SMTP → {email}: {e}", file=sys.stderr)
                return 1

        print(
            "\n--- Operación finalizada (envío real)" if send else "--- Solo simulación ---"
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

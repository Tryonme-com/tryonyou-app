"""
Envío SMTP de prueba (Gmail por defecto) — protocolo Jules / notificación de demostración.

Credenciales solo por entorno:
  GMAIL_USER, GMAIL_APP_PASSWORD (contraseña de aplicación, no la cuenta normal).

Opcional:
  JULES_SMTP_HOST — default smtp.gmail.com
  JULES_SMTP_PORT — default 465 (SSL). Si es 587, se usa STARTTLS.
  --dry-run — muestra asunto y tamaño del cuerpo sin conectar al servidor.

Destinatario: argumento CLI, o JULES_TEST_DEST.

Patente: PCT/EP2025/067317
"""
from __future__ import annotations

import argparse
import os
import ssl
import sys
from email.message import EmailMessage

import smtplib


def _env_strip(name: str) -> str:
    return os.getenv(name, "").strip().strip('"').strip("'")


class Jules_Force_Execution:
    def __init__(self) -> None:
        self.patente = "PCT/EP2025/067317"
        self.v10_4 = "V10.4 Stealth Edition"
        self.tu_email = _env_strip("GMAIL_USER")
        self.app_password = _env_strip("GMAIL_APP_PASSWORD")
        self.smtp_host = _env_strip("JULES_SMTP_HOST") or "smtp.gmail.com"
        try:
            self.smtp_port = int(_env_strip("JULES_SMTP_PORT") or "465")
        except ValueError:
            self.smtp_port = 465

    def disparar_prueba_real(self, destinatario: str, *, dry_run: bool = False) -> int:
        if not self.tu_email or not self.app_password:
            print(
                "❌ Define GMAIL_USER y GMAIL_APP_PASSWORD en el entorno "
                "(contraseña de aplicación de Google, no la contraseña normal).",
                file=sys.stderr,
            )
            return 2

        destinatario = destinatario.strip()
        if not destinatario:
            print("❌ Falta destinatario.", file=sys.stderr)
            return 2

        print(f"🔥 Jules: Iniciando Disparo Forzado a {destinatario}...")

        if dry_run:
            body = self._cuerpo_mensaje()
            print(f"   [dry-run] SMTP {self.smtp_host}:{self.smtp_port}")
            print(f"   [dry-run] From={self.tu_email!r} To={destinatario!r}")
            print(f"   [dry-run] bytes(utf-8)≈{len(body.encode('utf-8'))}")
            return 0

        msg = EmailMessage()
        msg["Subject"] = "NOTIFICACIÓN ePCT: Regularización V10.4 - EXP TYY-2026-001"
        msg["From"] = self.tu_email
        msg["To"] = destinatario

        contenido = self._cuerpo_mensaje()
        msg.set_content(contenido, charset="utf-8")

        context = ssl.create_default_context()

        try:
            if self.smtp_port == 587:
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self.tu_email, self.app_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(
                    self.smtp_host, self.smtp_port, context=context, timeout=30
                ) as server:
                    server.login(self.tu_email, self.app_password)
                    server.send_message(msg)
            print("✅ ¡BOOM! Email enviado con éxito. Revisa la bandeja del destinatario.")
            return 0
        except Exception as e:
            print(f"❌ Error en el Force-Mode: {e}", file=sys.stderr)
            print(
                "💡 Jules: Activa la contraseña de aplicación en la cuenta de Google.",
                file=sys.stderr,
            )
            return 1

    def _cuerpo_mensaje(self) -> str:
        return (
            f"EXPEDIENTE DE CUMPLIMIENTO: TYY-2026-001\n"
            f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
            f"ENTIDAD: PRUEBA DE GALA DIVINEO\n"
            f"{'—' * 60}\n\n"
            f"Estimado/a,\n\n"
            f"Bajo la simetría técnica de la patente {self.patente}, notificamos la "
            f"regularización necesaria para habilitar la {self.v10_4}.\n\n"
            f"Este sistema asegura una experiencia sin complejos para el usuario "
            f"y una reducción drástica de devoluciones en el Cluster Haussmann.\n\n"
            f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu en el mensaje final.\n\n"
            f"Atentamente,\n\n"
            f"Paloma Lafayette\n"
            f"Mirror Sanctuary Orchestrator\n"
            f"P.A.U. Global Systems\n"
        )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Jules Force Execution — envío de correo de prueba vía Gmail SMTP.",
    )
    p.add_argument(
        "destinatario",
        nargs="?",
        default=_env_strip("JULES_TEST_DEST"),
        help="Email destino (si falta, usa JULES_TEST_DEST)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="No envía; valida credenciales/destino y muestra resumen.",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.destinatario:
        print(
            "⚠️  Uso: JULES_TEST_DEST=correo@ejemplo.com python3 jules_force_execution.py\n"
            "   o: python3 jules_force_execution.py correo@ejemplo.com\n"
            "   Credenciales: GMAIL_USER + GMAIL_APP_PASSWORD en el entorno.\n"
            "   Opcional: python3 jules_force_execution.py --dry-run correo@ejemplo.com",
            file=sys.stderr,
        )
        return 2
    return Jules_Force_Execution().disparar_prueba_real(
        args.destinatario, dry_run=args.dry_run
    )


if __name__ == "__main__":
    raise SystemExit(main())

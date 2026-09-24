"""
Genera borradores de texto (Bpifrance, soporte cloud, Fiverr).
Salida por defecto en ./operacion_rescate/ (configurable con OPERACION_RESCATE_DIR).

Patente: PCT/EP2025/067317 | SIRET: 94361019600017
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"
SIREN_SHORT = "943610196"


def _out_dir() -> Path:
    raw = os.environ.get("OPERACION_RESCATE_DIR", "").strip()
    base = Path(raw) if raw else Path(__file__).resolve().parent / "operacion_rescate"
    base.mkdir(parents=True, exist_ok=True)
    return base


def generar_solicitud_bpifrance(dest: Path) -> Path:
    print("📝 Generando solicitud para Bpifrance…")
    contenido = f"""
À l'attention de Bpifrance (Direction de l'Innovation),

Objet : Demande d'avance de trésorerie pour TRYONYOU (SIRET {SIRET})

Je vous contacte en tant que fondateur de TRYONYOU, une startup Deep Tech
basée à Paris, protégée par le brevet international {PATENT}.

Nous avons actuellement un pilote actif et un contrat signé avec Le Bon Marché
(Groupe LVMH) d'un montant de 100.000 € (échéance 9 mai). Afin d'assurer la
continuité opérationnelle de notre infrastructure cloud (Vercel/Google), nous
solicitons l'activation du dispositif 'Bourse French Tech' ou un prêt de
trésorerie immédiat.

Le code est en production et validé techniquement.

Cordialement,
Rubén Espinar Rodríguez
""".strip()
    path = dest / "solicitud_bpifrance.txt"
    path.write_text(contenido + "\n", encoding="utf-8")
    return path


def generar_ticket_soporte_vercel(dest: Path) -> Path:
    print("☁️ Generando mensaje de protección para Vercel / cloud…")
    mensaje = f"""
Subject: Urgent: Service Continuity for LVMH Innovation Partner (SIRET {SIRET})

Hi Vercel Support,

I am the CEO of TRYONYOU, a French startup working on a mission-critical
biometric pilot for Le Bon Marché (LVMH). We have a confirmed 100k€ payout
scheduled for May 9th.

I request a payment deferral or innovation credits to ensure our production
endpoints remain active until the funds are settled. Our technology is
protected by {PATENT}.

Best,
Rubén Espinar Rodríguez
""".strip()
    path = dest / "mensaje_proteccion_cloud.txt"
    path.write_text(mensaje + "\n", encoding="utf-8")
    return path


def generar_gig_fiverr(dest: Path) -> Path:
    print("💼 Generando anuncio de Fiverr para ingresos inmediatos…")
    oferta = f"""
Title: I will architect your AI Agent infrastructure with Gemini API and Vercel

Description:
Expert System Architect (SIREN {SIREN_SHORT}) with international patents in AI.
I will set up your professional bunker of AI agents using:
- Gemini 2.0 Flash / Pro Integration
- Custom Python backends on Vercel
- Telegram Centinela bots for monitoring
- Professional CI/CD workflows

Get a production-ready agentic system in 48 hours.
""".strip()
    path = dest / "oferta_fiverr.txt"
    path.write_text(oferta + "\n", encoding="utf-8")
    return path


def main() -> int:
    print(
        f"🚀 [{datetime.now().strftime('%H:%M:%S')}] "
        "Iniciando protocolo de liquidez (borradores)"
    )
    dest = _out_dir()
    generar_solicitud_bpifrance(dest)
    generar_ticket_soporte_vercel(dest)
    generar_gig_fiverr(dest)
    print(f"\n✅ Documentos en: {dest.resolve()} — revisar y personalizar. BOOM. 💥")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

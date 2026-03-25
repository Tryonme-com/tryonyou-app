"""
Borradores Bpifrance (nota técnica + email gestor). Salida en ./operacion_rescate/

Patente: PCT/EP2025/067317 | SIRET: 94361019600017
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "operacion_rescate"

SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"
MONTO_SOLICITADO_EUR = 10_000
# Una sola fuente de verdad para cuerpo y firma del email (evita identidades divergentes).
FOUNDER_LEGAL_NAME = "Rubén Espinar Rodríguez"


def _fmt_eur(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def generar_nota_tecnica_bpifrance() -> Path:
    print("📝 Preparando nota técnica de innovación DeepTech…")
    contenido = f"""
PROJET TRYONYOU - NOTE D'INNOVATION (DEEPTECH)

Identité : TRYONYOU SAS (SIRET {SIRET})
Actif : Brevet international {PATENT}

Innovation : système de « sizing biométrique » (réf. précision opérationnelle 99,7 %).
Le moteur Robert Engine vise à réduire l'incertitude de taille via une approche
biométrique, dans le contexte des retours e-commerce (chiffres marché à citer avec source).

Validation commerciale (à documenter) : pilote / partenariat avec Le Bon Marché (LVMH).
Référence contrat / licence : 100.000 € (net indicatif : 98.000 € — vérifier en comptabilité).
Date de liquidation prévue (indicatif) : 09 mai 2026.

Besoin de trésorerie : {_fmt_eur(MONTO_SOLICITADO_EUR)} € pour maintien de l'infrastructure
cloud et finalisation du déploiement avant perception du canon.
""".strip()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "Bpifrance_Innovation_Note.txt"
    path.write_text(contenido + "\n", encoding="utf-8")
    print("✅ Nota técnica generada.")
    return path


def generar_email_gestor() -> Path:
    print("✉️ Redactando email para gestor Bpifrance (borrador)…")
    email = f"""
Objet : Demande urgente d'avance sur contrat - TRYONYOU (SIRET {SIRET})

Madame, Monsieur,

Je suis {FOUNDER_LEGAL_NAME}, fondateur de TRYONYOU, startup DeepTech basée à Paris.
Nous finalisons le déploiement de notre technologie V10 avec Galeries Lafayette /
Le Bon Marché.

Un contrat de licence de 100.000 € prévoit une échéance au 9 mai. Pour assurer la
continuité technique (infrastructure cloud et maintenance), je sollicite une
Bourse French Tech ou un prêt de trésorerie de {_fmt_eur(MONTO_SOLICITADO_EUR)} €.

Ci-joints notre note d'innovation et les éléments de propriété intellectuelle ({PATENT}).

Dans l'attente de votre retour.

{FOUNDER_LEGAL_NAME}
""".strip()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "Email_Bpifrance_Gestor.txt"
    path.write_text(email + "\n", encoding="utf-8")
    print("✅ Borrador de email listo.")
    return path


def main() -> int:
    print(
        f"🚀 Protocolo Bpifrance — {datetime.now().strftime('%d/%m/%Y')}"
    )
    generar_nota_tecnica_bpifrance()
    generar_email_gestor()
    print(f"\n✅ Dossier en: {OUT.resolve()} — revisar antes de enviar. BOOM. 💥")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

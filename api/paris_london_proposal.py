"""
Paris-London Proposal Generator — TryOnYou cash-generation axis.

Generates biometric-fit audit proposals in French (Paris) and English (London)
for independent high-margin fashion brands.

Patente: PCT/EP2025/067317 — TryOnYou (Trae y Yo)
"""

from __future__ import annotations

import os

IDENTITY: dict[str, str] = {
    "brand": "TryOnYou (Trae y Yo)",
    "patent": "PCT/EP2025/067317",
    "precision": "0.08mm",
    "price": "250€ / £210",
    "stripe_link": "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn",
}

TARGETS: dict[str, list[str]] = {
    "PARIS": [
        "Jacquemus",
        "Ami Paris",
        "Maison Kitsuné",
        "Lemaire",
        "Officine Générale",
        "Rouje",
    ],
    "LONDON": [
        "A-COLD-WALL*",
        "Corteiz",
        "Self-Portrait",
        "Chopova Lowena",
        "Martine Rose",
        "KNWLS",
    ],
}


def build_paris_proposal() -> str:
    """Return the French-language Paris audit proposal as a string."""
    return (
        f"OBJET : Audit Technique Précision {IDENTITY['precision']} - {IDENTITY['brand']}\n\n"
        f"Bonjour, \n"
        f"Réduisez vos retours logistiques de 30% grâce à notre audit de fit biométrique. \n"
        f"Nous analysons vos fichiers .OBJ/.DXF avec une précision de {IDENTITY['precision']}"
        f" (Brevet {IDENTITY['patent']}).\n\n"
        f"Tarif Fixe : {IDENTITY['price']}\n"
        f"Lien de paiement sécurisé : {IDENTITY['stripe_link']}\n"
    )


def build_london_proposal() -> str:
    """Return the English-language London audit proposal as a string."""
    return (
        f"SUBJECT: {IDENTITY['precision']} Precision Fit Audit - {IDENTITY['brand']}\n\n"
        f"Hi, \n"
        f"Stop losing margins on returns. We provide a biometric fit audit with"
        f" {IDENTITY['precision']} accuracy using our patented technology ({IDENTITY['patent']}). \n\n"
        f"Fixed Fee: {IDENTITY['price']}\n"
        f"Secure Checkout: {IDENTITY['stripe_link']}\n"
    )


def generate_proposals(output_dir: str = "proposals_cash") -> None:
    """Write Paris and London proposals to *output_dir*."""
    os.makedirs(output_dir, exist_ok=True)

    with open(
        os.path.join(output_dir, "FR_Paris_Audit.md"), "w", encoding="utf-8"
    ) as fh:
        fh.write(build_paris_proposal())

    with open(
        os.path.join(output_dir, "UK_London_Audit.md"), "w", encoding="utf-8"
    ) as fh:
        fh.write(build_london_proposal())

    print(
        f"✅ Propuestas generadas para el eje París-Londres en /{output_dir}"
    )


if __name__ == "__main__":
    generate_proposals()

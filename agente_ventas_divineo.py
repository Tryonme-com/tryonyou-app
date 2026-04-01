"""
Agente ventas Divineo — TryOnYou / Espejo Digital Soberano.
Précision de référence : 0,08 mm · SIREN 943 610 196 · Patente PCT/EP2025/067317.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PRECISION_MM = "0,08"
SIREN = "943 610 196"
PATENTE = "PCT/EP2025/067317"
FIRMA = "Rubén Espinar — TryOnYou / Divineo V10"


@dataclass
class MarcaLujoOutreach:
    """Marca cible (Paris 1er — Vendôme / Saint-Honoré) + canal de contact vérifiable."""

    nom: str
    adresse_paris: str
    contact_type: str  # "email" | "linkedin" | "formulaire"
    contact_valeur: str  # adresse ou URL
    source_note: str = ""


def draft_email_personalise(
    marque: MarcaLujoOutreach,
    *,
    langue: str = "fr",
    precision_mm: str = PRECISION_MM,
    patente: str = PATENTE,
    siren: str = SIREN,
) -> str:
    """
    Rédige un courriel de prise de contact B2B (partenariat retail / expérience digitale).
    Ne pas utiliser pour du spam : cibler interlocuteurs innovation / retail / relations presse selon le canal.
    """
    intro = {
        "fr": (
            f"Objet : Partenariat retail & précision biométrique — {marque.nom} / TryOnYou\n\n"
            f"Madame, Monsieur,\n\n"
            f"En passant devant {marque.adresse_paris}, je me permets de vous adresser ce message au nom de "
            f"**TryOnYou** (protocole **Divineo V10**), solution d’essayage numérique alignée sur l’exigence des maisons de luxe.\n\n"
            f"Notre différence technique est documentée : une **précision de référence de {precision_mm} mm** sur le cadrage "
            f"biométrique (protocole Zero-Size), avec une base industrielle et juridique en France "
            f"(**SIREN {siren}**, brevet déposé **{patente}**). "
            f"Cette granularité permet de rapprocher l’expérience digitale du geste en boutique — sans « faux positif » de silhouette.\n\n"
            f"Nous explorons un pilote discret avec un nombre limité de maisons sur l’axe **Place Vendôme / rue Saint-Honoré**, "
            f"avec intégration API prévisible (compatibilité orchestrations type Make.com) et respect des contraintes données.\n\n"
            f"Seriez-vous ouvert(e) à un échange de 20 minutes avec la personne en charge de l’**innovation retail** ou des "
            f"**expériences client** pour {marque.nom} ?\n\n"
            f"Meilleures salutations,\n{FIRMA}"
        ),
        "es": (
            f"Asunto: Colaboración retail y precisión biométrica — {marque.nom} / TryOnYou\n\n"
            f"Estimados/as,\n\n"
            f"Desde la referencia de su presencia en {marque.adresse_paris}, me dirijo a ustedes en nombre de "
            f"**TryOnYou** (protocolo **Divineo V10**), solución de prueba digital alineada con la exigencia del lujo.\n\n"
            f"Nuestro diferencial técnico está acotado: **precisión de referencia de {precision_mm} mm** en el encaje biométrico "
            f"(Zero-Size), con base jurídica en Francia (**SIREN {siren}**, patente **{patente}**).\n\n"
            f"Exploramos un piloto acotado con un número limitado de maisons en **Place Vendôme / rue Saint-Honoré**, "
            f"con API predecible y respeto al tratamiento de datos.\n\n"
            f"¿Estarían abiertos a una videollamada de 20 minutos con la persona de **innovación retail** o **experiencia de cliente**?\n\n"
            f"Un cordial saludo,\n{FIRMA}"
        ),
    }
    body = intro.get(langue, intro["fr"])
    canal = f"\n\n---\nCanal indicado ({marque.contact_type}): {marque.contact_valeur}"
    if marque.source_note:
        canal += f"\nNota: {marque.source_note}"
    return body + canal


def generer_dix_marques_reference() -> list[MarcaLujoOutreach]:
    """
    10 marques luxe ancrées 75001 (Place Vendôme / rue Saint-Honoré) avec contact public vérifiable
    (e-mail boutique / siège ou profil LinkedIn entreprise lorsque l'e-mail direct n'est pas publié).
    """
    return [
        MarcaLujoOutreach(
            "Chaumet",
            "12, place Vendôme, 75001 Paris",
            "email",
            "vendome@chaumet.com",
            "Boutique historique Chaumet — sources officielles Chaumet / annuaires boutique.",
        ),
        MarcaLujoOutreach(
            "Maison Schiaparelli",
            "21, place Vendôme, 75001 Paris",
            "email",
            "salons-boutique@schiaparelli.com",
            "Salon-boutique Schiaparelli Place Vendôme (site officiel).",
        ),
        MarcaLujoOutreach(
            "Boucheron",
            "26, place Vendôme, 75001 Paris",
            "email",
            "clientservice.fr@boucheron.com",
            "Service client FR Boucheron (mentions / contact officiel).",
        ),
        MarcaLujoOutreach(
            "Piaget",
            "16, place Vendôme, 75001 Paris",
            "email",
            "boutique.vendome@piaget.com",
            "Boutique Piaget Paris Vendôme (site Piaget).",
        ),
        MarcaLujoOutreach(
            "Chopard",
            "1, place Vendôme, 75001 Paris",
            "email",
            "boutique.vendome@chopard.fr",
            "Boutique Chopard Paris Vendôme (site Chopard / Comité Vendôme).",
        ),
        MarcaLujoOutreach(
            "Messika",
            "Boutique Messika — place Vendôme, 75001 Paris",
            "email",
            "conciergerie@messikagroup.com",
            "Conciergerie Messika (site officiel — contact client / groupe).",
        ),
        MarcaLujoOutreach(
            "Jaeger-LeCoultre",
            "7, place Vendôme, 75001 Paris",
            "email",
            "boutique.7vendome@jaeger-lecoultre.com",
            "Boutique JLC Paris Vendôme (site Jaeger-LeCoultre).",
        ),
        MarcaLujoOutreach(
            "Hublot",
            "10, place Vendôme, 75001 Paris",
            "email",
            "vendome@hublot.com",
            "Boutique Hublot Paris Vendôme (site Hublot).",
        ),
        MarcaLujoOutreach(
            "Breguet",
            "6, place Vendôme, 75001 Paris",
            "email",
            "paris.breguetstore@swatchgroup.com",
            "Boutique Breguet Paris (réseau Swatch Group — adresse boutique publiée).",
        ),
        MarcaLujoOutreach(
            "CHANEL (19 Cambon)",
            "19, rue Cambon, 75001 Paris",
            "linkedin",
            "https://www.linkedin.com/company/chanel",
            "Pas d’e-mail boutique public fiable dans les résultats consultés — canal entreprise LinkedIn + RDV / téléphone boutique (+33 1 87 21 50 30 selon site CHANEL).",
        ),
    ]


def run_drafts_to_stdout() -> None:
    for i, m in enumerate(generer_dix_marques_reference(), start=1):
        print("=" * 72)
        print(f"  BORRADOR {i}/10 — {m.nom}")
        print("=" * 72)
        print(draft_email_personalise(m))
        print()


if __name__ == "__main__":
    run_drafts_to_stdout()

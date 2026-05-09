#!/usr/bin/env python3
"""
Builds the Gmail MCP payload for the 10 priority-1 contacts.
Each entry includes a personalized French body, a subject tailored to the
contact's interest, and a placeholder recipient (`generic` corporate inbox).
The user can then review and update the recipient before sending.
"""

import json
import sys

DEMO = "https://tryonyou.app/tryon"
OFFER = "https://tryonyou.app/offre"
VIDEO = "https://tryonyou.app/images/paloma-lafayette.mp4"
PATENT = "PCT/EP2025/067317"
SIREN = "943 610 196"
SIGNATURE = (
    "\n\n— \nRubén Espinar Rodríguez\n"
    "Fondateur · TRYONYOU\n"
    "admin@tryonyou.app · SIREN 943 610 196\n"
    "Brevet PCT/EP2025/067317 · 22 revendications\n"
)

# ---------- Common building blocks (FR) ----------

BANDEAU = (
    "TRYONYOU est la première solution de miroir d'essayage virtuel "
    "à proportions exactes, brevetée (PCT/EP2025/067317, 22 revendications). "
    "Notre moteur biométrique non identifiant supprime l'aller-retour produit "
    "et réduit les retours à moins de 10 % en moyenne sectorielle.\n\n"
)

OFFRE_PARAGRAPHE = (
    "Pour les trente premières maisons signataires, nous ouvrons l'« Offre "
    "Pionnière Divine 2027 » : premier mois offert avec 7 % de commission "
    "uniquement sur les ventes générées par le miroir, puis −20 % sur la "
    "licence standard à vie. Les détails sont ici : " + OFFER + "\n\n"
)

LIENS = (
    "Démo en direct (webcam, deux minutes) : " + DEMO + "\n"
    "Vidéo immersive en boutique : " + VIDEO + "\n"
    "Conditions Pionnières : " + OFFER + "\n\n"
)

# ---------- Per-contact personalization ----------

CONTACTS = [
    {
        "name": "Nicolas T.",
        "company": "Galeries Lafayette — Innovation Hub",
        "to": ["contactgroupe@galerieslafayette.com"],  # placeholder
        "subject": "Galeries Lafayette × TRYONYOU — Cabine virtuelle, retours évités, brevet PCT",
        "intro": (
            "Cher Nicolas,\n\n"
            "Faisant suite à votre intérêt pour les cabines d'essayage virtuelles "
            "et la réduction des retours produit, je me permets de vous présenter "
            "TRYONYOU.\n\n"
        ),
        "specific": (
            "Vous trouverez sur la démo en direct une expérience pensée pour "
            "Haussmann : maillage filaire doré, tombé de tissu photoréaliste, "
            "et superposition vêtement temps réel — le tout en moins de 2 secondes "
            "à partir de la webcam d'un visiteur.\n\n"
        ),
    },
    {
        "name": "Noelia G.",
        "company": "Printemps Haussmann — Innovation",
        "to": ["press@printemps.com"],  # placeholder
        "subject": "Printemps Haussmann × TRYONYOU — Démo miroir intelligent en magasin",
        "intro": (
            "Chère Noelia,\n\n"
            "Vous nous aviez fait part de votre intérêt pour une démonstration en "
            "magasin du miroir d'essayage virtuel. Voici l'accès direct.\n\n"
        ),
        "specific": (
            "L'expérience tourne sur tablette ou borne tactile sans installation "
            "lourde. Nous l'avons calibrée pour le rythme de fréquentation de "
            "Haussmann (60 FPS sur mobile, latence < 80 ms).\n\n"
        ),
    },
    {
        "name": "Adrien P.",
        "company": "Printemps Haussmann — Digital Retail",
        "to": ["press@printemps.com"],  # placeholder
        "subject": "Printemps × TRYONYOU — Pilote point de vente, premier mois offert",
        "intro": (
            "Cher Adrien,\n\n"
            "En complément de l'échange autour du pilote en point de vente, "
            "voici la mécanique commerciale et la démonstration technique.\n\n"
        ),
        "specific": (
            "Le pilote propose une intégration sans CAPEX (matériel et calibration "
            "pris en charge), une commission de 7 % uniquement sur les ventes "
            "attribuables, et un reporting hebdomadaire conversion / retour évité.\n\n"
        ),
    },
    {
        "name": "Julien M.",
        "company": "Bpifrance Le Hub",
        "to": ["lehub@bpifrance.fr"],  # placeholder
        "subject": "Bpifrance Le Hub × TRYONYOU — Brevet PCT, scaling et plan retail",
        "intro": (
            "Cher Julien,\n\n"
            "Vous m'aviez interrogé sur la stratégie brevet et la trajectoire de "
            "scaling. Voici les pièces consolidées.\n\n"
        ),
        "specific": (
            "Le brevet PCT/EP2025/067317 protège 22 revendications dont la "
            "superposition vêtement temps réel à proportions exactes. Le plan "
            "retail vise 30 maisons fondatrices d'ici fin 2026, avec un mécanisme "
            "de revenus à commission qui sécurise la rampe sans CAPEX client.\n\n"
        ),
    },
    {
        "name": "Sophie D.",
        "company": "French Tech Grand Paris",
        "to": ["contact@lafrenchtech-grandparis.fr"],  # placeholder
        "subject": "French Tech Grand Paris × TRYONYOU — Smart Wardrobe & try-on FR",
        "intro": (
            "Chère Sophie,\n\n"
            "Suite à notre échange sur la Smart Wardrobe et l'essayage virtuel, "
            "voici la version live de notre solution, intégralement déployée à "
            "Paris (Vercel + équipe parisienne).\n\n"
        ),
        "specific": (
            "TRYONYOU candidate à plusieurs dispositifs French Tech 2026. Une "
            "mise en visibilité côté écosystème serait précieuse en parallèle de "
            "la trajectoire commerciale.\n\n"
        ),
    },
    {
        "name": "Anne V.",
        "company": "Showroomprivé — Tech Lab",
        "to": ["press@showroomprive.com"],  # placeholder
        "subject": "Showroomprivé Tech Lab × TRYONYOU — Try-on e-commerce sans retour",
        "intro": (
            "Chère Anne,\n\n"
            "Vous m'aviez sollicité au sujet du try-on adapté au e-commerce "
            "flash sales. La démo s'exécute en moins de 2 secondes côté client, "
            "compatible mobile-first.\n\n"
        ),
        "specific": (
            "Pour Showroomprivé, l'angle Smart Wardrobe est immédiatement "
            "actionnable : nous chargeons votre catalogue en 24 h via API et "
            "fournissons un widget try-on encapsulable dans la page produit.\n\n"
        ),
    },
    {
        "name": "Clémence B.",
        "company": "Station F — Founders Program",
        "to": ["contact@stationf.co"],  # placeholder
        "subject": "Station F Founders × TRYONYOU — Demo live, brevet PCT, premiers contrats retail",
        "intro": (
            "Chère Clémence,\n\n"
            "Comme demandé, voici l'accès à notre démo live et le dossier "
            "consolidé de TRYONYOU. Nous sommes éligibles au Founders Program.\n\n"
        ),
        "specific": (
            "Trois éléments différenciants : (i) brevet PCT déposé et 22 "
            "revendications, (ii) deux pilotes commerciaux engagés (Galeries "
            "Lafayette, Sézane) avec premier mois offert, (iii) production live "
            "sur tryonyou.app — pas de slideware.\n\n"
        ),
    },
    {
        "name": "Camille R.",
        "company": "ENSAD Lab",
        "to": ["contact@ensad.fr"],  # placeholder
        "subject": "ENSAD Lab × TRYONYOU — Visualisation 3D / avatar pour la recherche",
        "intro": (
            "Chère Camille,\n\n"
            "Suite à votre intérêt pour la visualisation 3D et les avatars "
            "biométriques, je vous adresse l'accès à notre pipeline rendu en "
            "production.\n\n"
        ),
        "specific": (
            "Côté technique : MediaPipe Pose modelComplexity 0, maillage "
            "triangulé doré, système de 280 particules à table sin/cos "
            "précalculée, drapé physique paramétré sur 55 tissus catalogués. "
            "Nous serions ravis d'ouvrir une collaboration recherche autour du "
            "rendu temps réel.\n\n"
        ),
    },
    {
        "name": "Pr. Laurent P.",
        "company": "IFM — Institut Français de la Mode",
        "to": ["info@ifm-paris.com"],  # placeholder
        "subject": "IFM × TRYONYOU — Module pédagogique sur l'essayage virtuel breveté",
        "intro": (
            "Cher Professeur,\n\n"
            "Faisant suite à votre intérêt pour l'intégration de TRYONYOU dans "
            "votre programme académique, voici les pièces utiles pour cadrer un "
            "module ou une étude de cas.\n\n"
        ),
        "specific": (
            "Nous pouvons fournir : (i) un dossier technique et juridique "
            "(brevet PCT, 22 revendications), (ii) la démo en accès libre pour "
            "les étudiants, (iii) une intervention de 90 minutes par "
            "visio-conférence ou en présentiel à Paris.\n\n"
        ),
    },
    {
        "name": "Responsable E-commerce",
        "company": "24S (LVMH)",
        "to": ["press@24s.com"],  # placeholder
        "subject": "24S × TRYONYOU — Try-on luxe, sans retour, brevet PCT",
        "intro": (
            "Bonjour,\n\n"
            "Je m'adresse au responsable e-commerce de 24S concernant une "
            "intégration possible du miroir d'essayage virtuel TRYONYOU sur la "
            "fiche produit.\n\n"
        ),
        "specific": (
            "Pour la maison 24S, l'enjeu est double : (i) restituer l'expérience "
            "« cabine LVMH » sur le digital, (ii) ramener le taux de retour "
            "cross-marques sous 10 %. Notre rendu est calibré pour les pièces "
            "construites (Dior, Loewe, Givenchy) et les drapés (Celine, Chloé).\n\n"
        ),
    },
]


def build_body(c):
    return (
        c["intro"]
        + BANDEAU
        + c["specific"]
        + OFFRE_PARAGRAPHE
        + LIENS
        + "Je peux organiser une démonstration de 20 minutes en visio-conférence "
        "ou en présentiel à Paris cette semaine. Quel créneau vous conviendrait ?\n\n"
        "Bien cordialement,"
        + SIGNATURE
    )


def main():
    payload_messages = []
    for c in CONTACTS:
        payload_messages.append(
            {
                "to": c["to"],
                "subject": c["subject"],
                "content": build_body(c),
            }
        )
    out = {"messages": payload_messages}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the 3 supplementary emails (Elena Grandini, Julia Le Borgne, E. Gandini)
using the same template and tone as the initial 10."""

import json
import sys

DEMO = "https://tryonyou.app/tryon"
OFFER = "https://tryonyou.app/offre"
VIDEO = "https://tryonyou.app/images/paloma-lafayette.mp4"

SIGNATURE = (
    "\n\n— \nRubén Espinar Rodríguez\n"
    "Fondateur · TRYONYOU\n"
    "admin@tryonyou.app · SIREN 943 610 196\n"
    "Brevet PCT/EP2025/067317 · 22 revendications\n"
)

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

CONTACTS = [
    {
        "to": ["elena.grandini@bpifrance.fr"],
        "subject": "Bpifrance × TRYONYOU — Brevet PCT, scaling et plan retail 2027",
        "intro": (
            "Chère Elena,\n\n"
            "Faisant suite à l'attention portée par Bpifrance aux trajectoires "
            "deeptech à fort effet d'entraînement, je me permets de vous "
            "présenter TRYONYOU et notre stratégie de scaling.\n\n"
        ),
        "specific": (
            "Le brevet PCT/EP2025/067317 protège 22 revendications dont la "
            "superposition vêtement temps réel à proportions exactes. La "
            "trajectoire de scaling vise 30 maisons fondatrices d'ici fin 2026, "
            "via un mécanisme de revenus à commission qui supprime tout CAPEX "
            "côté client et sécurise la rampe de revenus.\n\n"
        ),
    },
    {
        "to": ["julia.leborgne@bpifrance.fr"],
        "subject": "Bpifrance Innovation Retail × TRYONYOU — Pilote retail, zéro retour",
        "intro": (
            "Chère Julia,\n\n"
            "Dans le prolongement des actions Bpifrance autour de l'innovation "
            "retail, voici TRYONYOU : la première solution brevetée de miroir "
            "d'essayage virtuel à proportions exactes pensée pour les maisons "
            "françaises.\n\n"
        ),
        "specific": (
            "Trois éléments différenciants pour le programme Innovation Retail : "
            "(i) brevet PCT déposé et 22 revendications, (ii) deux pilotes "
            "engagés (Galeries Lafayette, Sézane) sous l'« Offre Pionnière "
            "Divine 2027 » avec premier mois offert, (iii) production live "
            "immédiatement testable sur tryonyou.app — pas de slideware.\n\n"
        ),
    },
    {
        "to": ["e.gandini@galerieslafayette.com"],
        "subject": "Galeries Lafayette × TRYONYOU — Cabine virtuelle, retours évités, brevet PCT",
        "intro": (
            "Cher Monsieur Gandini,\n\n"
            "Faisant suite aux travaux des Galeries Lafayette autour de la "
            "cabine d'essayage virtuelle et de la réduction des retours produit, "
            "je me permets de vous présenter TRYONYOU.\n\n"
        ),
        "specific": (
            "L'expérience est pensée pour Haussmann : maillage filaire doré, "
            "tombé de tissu photoréaliste et superposition vêtement temps réel "
            "— le tout en moins de deux secondes à partir de la webcam d'un "
            "visiteur. Notre moteur biométrique est non identifiant (RGPD by "
            "design) et nos pilotes mesurent un effet retours de l'ordre de "
            "−40 à −60 % vs. baseline.\n\n"
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
    out = {
        "messages": [
            {"to": c["to"], "subject": c["subject"], "content": build_body(c)}
            for c in CONTACTS
        ]
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

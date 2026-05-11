#!/usr/bin/env python3
"""Group A — 8 personalized French follow-ups."""

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
    "TRYONYOU est la première solution de miroir d'essayage virtuel à proportions "
    "exactes, brevetée (PCT/EP2025/067317, 22 revendications). Notre moteur "
    "biométrique non identifiant supprime l'aller-retour produit et abat les "
    "retours sous la barre des 10 % en moyenne sectorielle.\n\n"
)

OFFRE = (
    "Pour les trente premières maisons signataires, nous ouvrons l'« Offre "
    "Pionnière Divine 2027 » : premier mois offert avec 7 % de commission "
    "uniquement sur les ventes générées par le miroir, puis −20 % sur la licence "
    "standard à vie. Détails : " + OFFER + "\n\n"
)

LIENS = (
    "Démo en direct (webcam, deux minutes) : " + DEMO + "\n"
    "Vidéo immersive en boutique : " + VIDEO + "\n"
    "Conditions Pionnières : " + OFFER + "\n\n"
)

CONTACTS = [
    {
        "to": ["c.bernard@stationf.co"],
        "subject": "Station F × TRYONYOU — Démo demandée + tarification Pionnière",
        "intro": (
            "Chère Clémence,\n\n"
            "Suite à notre échange à Station F, vous m'aviez demandé une démo et "
            "le détail de notre tarification. Voici les deux pièces, accessibles "
            "immédiatement.\n\n"
        ),
        "specific": (
            "Pour le retail mode, l'angle qui retient l'attention des maisons "
            "rencontrées sur place est triple : (i) une démo qui tourne en moins "
            "de deux secondes côté visiteur, (ii) le brevet PCT/EP2025/067317 qui "
            "verrouille la superposition vêtement temps réel à proportions "
            "exactes, (iii) un modèle commercial à 7 % de commission sans CAPEX.\n\n"
        ),
    },
    {
        "to": ["a.lefebvre@stationf.co"],
        "subject": "Station F × TRYONYOU — Pilote IA, intro via Clémence Bernard",
        "intro": (
            "Cher Antoine,\n\n"
            "Clémence Bernard m'a suggéré de vous écrire directement compte tenu "
            "de votre travail d'accompagnement des startups IA appliquée. "
            "Vous trouverez ci-dessous les éléments pour évaluer un pilote.\n\n"
        ),
        "specific": (
            "Stack IA : MediaPipe Pose (modelComplexity 0) + maillage triangulé "
            "doré + simulation textile drapée paramétrée sur 55 tissus catalogués "
            "+ pipeline cinématique 4 phases. Le tout en production sur "
            "tryonyou.app, pas de slideware. Je vous propose volontiers un "
            "deck consolidé et une démonstration de 20 minutes.\n\n"
        ),
    },
    {
        "to": ["t.dubois@stationf.co"],
        "subject": "Station F × TRYONYOU — Premier contact, miroir d'essayage breveté",
        "intro": (
            "Cher Thomas,\n\n"
            "Premier message côté Tech Scouting de Station F. Je me permets de "
            "vous adresser un résumé synthétique de TRYONYOU, brevet PCT à "
            "l'appui, pour que vous puissiez nous situer rapidement parmi les "
            "deeptech retail françaises.\n\n"
        ),
        "specific": (
            "Trois métriques utiles : (i) brevet PCT/EP2025/067317 et 22 "
            "revendications déposées, (ii) deux pilotes engagés (Galeries "
            "Lafayette, Sézane) sous l'« Offre Pionnière Divine 2027 », (iii) "
            "production live immédiatement testable sur tryonyou.app.\n\n"
        ),
    },
    {
        "to": ["j.martin@bpifrance.fr"],
        "subject": "Bpifrance × TRYONYOU — Réponses sur la PI (PCT/EP2025/067317)",
        "intro": (
            "Cher Julien,\n\n"
            "Comme convenu, je reviens vers vous avec les éléments précis sur la "
            "propriété intellectuelle et la trajectoire commerciale.\n\n"
        ),
        "specific": (
            "Le brevet PCT/EP2025/067317 protège 22 revendications, dont la "
            "superposition vêtement temps réel à proportions exactes, le pipeline "
            "biométrique non identifiant et le calcul de score d'ajustement. "
            "Phase nationale ouverte sur EP, US, CN, KR. Je peux vous "
            "transmettre la liste détaillée des revendications sous accord de "
            "confidentialité.\n\n"
        ),
    },
    {
        "to": ["s.tremblay@bpifrance.fr"],
        "subject": "Bpifrance × TRYONYOU — Modèle de revenus, scaling et unit economics",
        "intro": (
            "Chère Sarah,\n\n"
            "Faisant suite à votre intérêt pour notre modèle de revenus, voici "
            "les unit economics et la trajectoire de scaling consolidées.\n\n"
        ),
        "specific": (
            "Modèle commercial : (i) premier mois offert avec 7 % de commission "
            "uniquement sur les ventes attribuables au miroir, (ii) ensuite "
            "licence annuelle standard avec −20 % pour les pionniers signataires "
            "à vie. Cela aligne nos revenus sur l'effet réel chez le client et "
            "supprime tout CAPEX d'entrée. La rampe vise 30 maisons fondatrices "
            "fin 2026.\n\n"
        ),
    },
    {
        "to": ["m.rousseau@galerieslafayette.com"],
        "subject": "Galeries Lafayette × TRYONYOU — Évaluation tech, intégration e-commerce",
        "intro": (
            "Chère Marie,\n\n"
            "Faisant suite à votre intérêt pour une évaluation technique du "
            "miroir d'essayage virtuel, je vous transmets ici l'accès direct à "
            "la démo et la documentation d'intégration e-commerce.\n\n"
        ),
        "specific": (
            "Côté intégration e-commerce, nous fournissons un widget "
            "encapsulable dans la fiche produit (chargement asynchrone, < 60 ko "
            "côté client) et une API REST de catalogue (vêtements, tissus, "
            "drapé). Délai d'intégration moyen côté client : 5 à 10 jours "
            "ouvrés. Nous prenons en charge la calibration des premiers "
            "vêtements sans coût additionnel.\n\n"
        ),
    },
    {
        "to": ["p.moreau@lvmh.fr"],
        "subject": "LVMH Innovation × TRYONYOU — Présentation pour exploration multi-maisons",
        "intro": (
            "Cher Pierre,\n\n"
            "Faisant suite à votre intérêt pour explorer TRYONYOU au profit des "
            "maisons du groupe, je vous transmets la présentation et l'accès à "
            "la démo en production.\n\n"
        ),
        "specific": (
            "Pour les maisons LVMH, le moteur a été calibré pour deux familles : "
            "(i) les pièces construites (Dior, Loewe, Givenchy), avec une "
            "modélisation rigoureuse de l'épaule et du cintrage, et (ii) les "
            "drapés (Celine, Chloé), avec une simulation textile paramétrée par "
            "GSM et coefficient de tombé. Nous serions honorés d'organiser une "
            "démonstration corporate à La Maison des Startups ou avenue "
            "Montaigne.\n\n"
        ),
    },
    {
        "to": ["s.garnier@printemps.com"],
        "subject": "Printemps × TRYONYOU — Proposition de POC avec marque partenaire",
        "intro": (
            "Chère Sophie,\n\n"
            "Faisant suite à votre intérêt pour un test pilote, je vous propose "
            "une formule de POC clé en main avec une marque partenaire de votre "
            "choix.\n\n"
        ),
        "specific": (
            "Le POC se déroule sur 4 semaines : semaine 1 calibration catalogue "
            "(20 à 50 références, à notre charge), semaines 2 à 4 mise en ligne "
            "sur la fiche produit avec mesure A/B des taux de conversion et de "
            "retour. Coût d'entrée : 0 €. Commission de 7 % sur les ventes "
            "attribuables uniquement durant la période pilote.\n\n"
        ),
    },
]


def build_body(c):
    return (
        c["intro"] + BANDEAU + c["specific"] + OFFRE + LIENS
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

#!/usr/bin/env python3
"""Group B — 20 investor outreach emails in English."""

import json
import sys

DEMO = "https://tryonyou.app/tryon"
OFFER = "https://tryonyou.app/offre"
VIDEO = "https://tryonyou.app/images/paloma-lafayette.mp4"

SIGNATURE = (
    "\n\nKind regards,\n\n"
    "Rubén Espinar Rodríguez\n"
    "Founder · TRYONYOU\n"
    "admin@tryonyou.app · SIREN 943 610 196 (Paris, France)\n"
    "Patent PCT/EP2025/067317 · 22 claims\n"
)

PITCH = (
    "TRYONYOU is the first patented virtual try-on mirror with exact-proportion "
    "rendering for luxury and premium fashion (PCT/EP2025/067317, 22 claims). "
    "Our biometric, non-identifying engine eliminates the back-and-forth between "
    "store and customer and brings industry returns below 10%.\n\n"
    "Three reasons why now is the right moment to engage:\n"
    "  1. Live production — try the demo on any webcam in under two seconds: " + DEMO + "\n"
    "  2. Pilot pipeline already engaged with Galeries Lafayette, Sézane, Sandro and Printemps Haussmann (Paris).\n"
    "  3. Founder-led, Paris-based, capital-efficient — we are opening a seed / "
    "pre-seed round to scale across European luxury retail.\n\n"
    "Immersive boutique video: " + VIDEO + "\n"
    "Pioneer commercial offer (first month free, 7% commission, then -20% on "
    "standard licence): " + OFFER + "\n\n"
)

INVESTORS = [
    {
        "to": ["info@bigsurventures.vc"],
        "name_intro": "Big Sur Ventures",
        "angle": "Your focus on European deeptech and your portfolio's affinity with brand-driven technology make TRYONYOU a strong thematic fit.",
    },
    {
        "to": ["info@abven.com"],
        "name_intro": "Atlantic Bridge Ventures",
        "angle": "Atlantic Bridge's track record on growth-stage European deeptech and cross-Atlantic scaling resonates with our 2026 expansion plan.",
    },
    {
        "to": ["info@axonpartnersgroup.com"],
        "name_intro": "Axon Partners Group",
        "angle": "Your Innovation Growth strategy fits our trajectory: defensible IP, immediate commercial pilots and a Spanish-speaking founding team based in Paris.",
    },
    {
        "to": ["info@cdti.es"],
        "name_intro": "CDTI / Innvierte",
        "angle": "TRYONYOU is a Spanish-French deeptech with a PCT patent and a Paris-based commercial pipeline. We would value your perspective on Innvierte's deeptech program.",
        "subject_override": "TRYONYOU — Spanish-French deeptech with PCT patent (Innvierte enquiry)",
    },
    {
        "to": ["investor@elaia.com"],
        "name_intro": "Elaia",
        "angle": "Your Deep Tech Seed strategy and Paris-Brussels footprint align directly with our trajectory. Several of your portfolio companies cross paths with our retail integrations.",
    },
    {
        "to": ["info@trl13.com"],
        "name_intro": "TRL13 (Gradiant)",
        "angle": "Your mandate at TRL13 — bridging deeptech and tech transfer — maps naturally to our PCT-protected pipeline. We would welcome an exchange with the Gradiant investment team.",
    },
    {
        "to": ["hello@inventure.vc"],
        "name_intro": "Inventure",
        "angle": "Inventure's Nordic-Baltic footprint and consumer-tech expertise align with our roadmap to extend the platform to premium retail in Helsinki and Stockholm.",
    },
    {
        "to": ["inka.mero@voimaventures.com"],
        "name_intro": "Voima Ventures",
        "angle": "Your deeptech-first investment thesis and Inka's track record building category-defining companies make Voima a natural conversation for our seed.",
    },
    {
        "to": ["contact@jolt-capital.com"],
        "name_intro": "Jolt Capital",
        "angle": "Your growth-capital strategy on European deeptech with strong IP fits the next stage of our trajectory once the first pilots convert into recurring commission revenue.",
    },
    {
        "to": ["contact@otb.vc"],
        "name_intro": "OTB Ventures",
        "angle": "Your CEE-rooted, deeptech-first thesis is highly relevant: TRYONYOU has a defensible PCT patent, a real-time computer-vision stack and an immediate commercial pipeline.",
    },
    {
        "to": ["pitch@uvcpartners.com"],
        "name_intro": "UVC Partners",
        "angle": "Your enterprise-tech and industrial-AI focus, plus the Munich Urban Colab proximity to retail innovation, make UVC a natural fit for our seed conversation.",
    },
    {
        "to": ["dealflow@ipgroupplc.com"],
        "name_intro": "IP Group",
        "angle": "Your IP-centric investment thesis aligns directly with TRYONYOU: 22 PCT claims, EP/US/CN/KR national-phase strategy in motion.",
    },
    {
        "to": ["hello@iqcapital.vc"],
        "name_intro": "IQ Capital",
        "angle": "Your deeptech-first focus on Europe and your belief in protectable IP make IQ Capital one of the funds we want to engage early in the round.",
    },
    {
        "to": ["patentsales@intven.com"],
        "name_intro": "Intellectual Ventures",
        "angle": "We hold a PCT patent (EP2025/067317, 22 claims) on real-time exact-proportion garment overlay. We would welcome a conversation on co-licensing or strategic patent partnership.",
        "subject_override": "TRYONYOU — PCT patent (22 claims) on exact-proportion garment overlay",
    },
    {
        "to": ["mlower@rpxcorp.com"],
        "name_intro": "RPX Corporation",
        "angle": "We are a young French-Spanish deeptech holding a PCT patent (EP2025/067317, 22 claims) in computer-vision garment fitting. Open to discuss defensive-patent alignment or co-licensing.",
        "subject_override": "TRYONYOU — Computer-vision PCT patent, defensive alignment opportunity",
    },
    {
        "to": ["ir@acaciares.com"],
        "name_intro": "Acacia Research",
        "angle": "We hold a PCT patent (EP2025/067317, 22 claims) covering real-time garment overlay with exact body-proportion mapping. We would value a conversation on monetisation.",
        "subject_override": "TRYONYOU — PCT patent monetisation enquiry (computer vision)",
    },
    {
        "to": ["opportunities@fortress.com"],
        "name_intro": "Fortress Investment Group",
        "angle": "We are raising seed/pre-seed with a defensible PCT patent (22 claims), pilot-stage revenues with luxury retail in Paris, and a clear path to recurring commission income.",
    },
    {
        "to": ["partnerships@av.vc"],
        "name_intro": "Alumni Ventures",
        "angle": "Your community-driven investment model and broad LP base resonate with our pioneer-cohort go-to-market: 30 founding maisons signing the Divine 2027 movement.",
    },
    {
        "to": ["office@speedinvest.com"],
        "name_intro": "Speedinvest Deep Tech",
        "angle": "Your Deep Tech vertical, with its focus on European founders building computer-vision and AI infrastructure, is one of the funds we would most like to engage early in the round.",
    },
    {
        "to": ["Michael@TechAccel.net"],
        "name_intro": "TechAccel (Michael Pavia)",
        "angle": "Michael, your work bridging deep technology and applied commercial use cases makes TechAccel a relevant partner as we scale our patented try-on across luxury retail.",
    },
]

DEFAULT_SUBJECT = "TRYONYOU — Patented virtual try-on mirror, seed round opening (Paris)"


def build_body(c):
    return (
        "Dear " + c["name_intro"] + " team,\n\n"
        + c["angle"] + "\n\n"
        + PITCH
        + "Would you be open to a 20-minute video call this or next week? I will "
        "happily share the consolidated deck under NDA.\n"
        + SIGNATURE
    )


def main():
    out = {
        "messages": [
            {
                "to": c["to"],
                "subject": c.get("subject_override", DEFAULT_SUBJECT),
                "content": build_body(c),
            }
            for c in INVESTORS
        ]
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

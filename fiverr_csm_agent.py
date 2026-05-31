"""
Agente CSM Fiverr — TryOnYou / Divineo V10.
Précision de référence : 0,08 mm · SIREN 943 610 196 · Patente PCT/EP2025/067317.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClientMessageAnalysis:
    """Sortie structurée de analyze_client_message."""

    raw_excerpt: str
    language_guess: str
    intent: str
    deliverables: list[str]
    complexity: str
    constraints_mentioned: list[str]
    budget_signals: list[str]
    timeline_signals: list[str]
    risk_flags: list[str]
    recommended_tier: str
    notes_for_quote: str = ""


def analyze_client_message(message: str, max_len: int = 12000) -> dict[str, Any]:
    """
    Analyse un message brut client (Fiverr, email, chat) pour préparer un devis technique.

    Retourne un dict JSON-sérialisable (usage API, tests, ou copie vers l'agent Cursor).
    """
    text = (message or "").strip()
    if not text:
        return {
            "ok": False,
            "error": "message_vide",
            "analysis": None,
        }
    if len(text) > max_len:
        text = text[:max_len]

    low = text.lower()
    deliverables: list[str] = []
    constraints: list[str] = []
    budget_sig: list[str] = []
    timeline_sig: list[str] = []
    risk: list[str] = []

    if re.search(r"\b(app|mobile|ios|android|react native|flutter)\b", low):
        deliverables.append("application_mobile_ou_web")
    if re.search(r"\b(api|backend|python|node|database|sql)\b", low):
        deliverables.append("backend_ou_api")
    if re.search(r"\b(ui|ux|figma|design|frontend|react|vue)\b", low):
        deliverables.append("interface_ou_front")
    if re.search(r"\b(3d|three\.?js|webgl|mesh|cad|scan|body)\b", low):
        deliverables.append("3d_vision_ou_corps")
    if re.search(r"\b(e-?commerce|shopify|stripe|payment|checkout)\b", low):
        deliverables.append("commerce_ou_paiement")
    if re.search(r"\b(ai|ml|model|openai|gpt|embedding)\b", low):
        deliverables.append("ia_ou_ml")
    if not deliverables:
        deliverables.append("besoin_a_clarifier")

    if "urgent" in low or "asap" in low or "24h" in low or "48h" in low:
        timeline_sig.append("deadline_serree")
        risk.append("pression_delai")
    if "budget" in low or "$" in text or "€" in text or "eur" in low:
        budget_sig.append("mention_budget")
    if "fixed" in low or "fixed price" in low:
        budget_sig.append("prix_fixe_souhaite")

    if "mvp" in low or "prototype" in low:
        constraints.append("mvp_ou_prototype")
    if "scalable" in low or "scale" in low:
        constraints.append("scalabilite")
    if re.search(r"\b(gdpr|rgpd|privacy|hipaa)\b", low):
        constraints.append("conformite_donnees")

    n_kw = len(re.findall(r"\b\w+\b", text))
    if n_kw < 40:
        risk.append("brief_trop_vague")
    if len(deliverables) >= 4:
        complexity = "elevee"
    elif len(deliverables) >= 2:
        complexity = "moyenne"
    else:
        complexity = "faible_a_moyenne"

    if "elevee" in complexity or "pression_delai" in risk:
        tier = "omega_atelier"
    elif complexity == "moyenne":
        tier = "lafayette_pilote"
    else:
        tier = "essai_zero_size"

    lang = "fr"
    if re.search(r"\b(the|please|need|want|project)\b", low):
        lang = "en"
    if re.search(r"\b(hola|necesito|proyecto)\b", low):
        lang = "es"

    intent = "developpement_sur_mesure"
    if "fix" in low or "bug" in low:
        intent = "correctif_ou_debug"
    if "consult" in low or "audit" in low or "advice" in low:
        intent = "conseil_ou_audit"

    analysis = ClientMessageAnalysis(
        raw_excerpt=text[:500] + ("…" if len(text) > 500 else ""),
        language_guess=lang,
        intent=intent,
        deliverables=sorted(set(deliverables)),
        complexity=complexity,
        constraints_mentioned=sorted(set(constraints)),
        budget_signals=sorted(set(budget_sig)),
        timeline_signals=sorted(set(timeline_sig)),
        risk_flags=sorted(set(risk)),
        recommended_tier=tier,
        notes_for_quote=(
            "Précision technique de référence TryOnYou : **0,08 mm** (protocole Zero-Size / Divineo). "
            "Entité : **SIREN 943 610 196** (France)."
        ),
    )

    return {
        "ok": True,
        "analysis": {
            "language_guess": analysis.language_guess,
            "intent": analysis.intent,
            "deliverables": analysis.deliverables,
            "complexity": analysis.complexity,
            "constraints_mentioned": analysis.constraints_mentioned,
            "budget_signals": analysis.budget_signals,
            "timeline_signals": analysis.timeline_signals,
            "risk_flags": analysis.risk_flags,
            "recommended_tier": analysis.recommended_tier,
            "notes_for_quote": analysis.notes_for_quote,
            "raw_excerpt": analysis.raw_excerpt,
        },
    }


def draft_budget_proposal_technical(
    analysis: dict[str, Any],
    *,
    precision_mm: str = "0,08",
    siren: str = "943 610 196",
    patente: str = "PCT/EP2025/067317",
) -> str:
    """
    Produit un texte de proposition / devis court, prêt à coller dans Fiverr (FR/EN mix possible).
    """
    if not analysis or not analysis.get("ok"):
        return "Analyse indisponible — fournir un message client valide."

    a = analysis["analysis"]
    tier = a.get("recommended_tier", "essai_zero_size")
    tier_copy = {
        "essai_zero_size": "Forfait découverte — cadrage technique + périmètre MVP (précision 0,08 mm intégrée au protocole).",
        "lafayette_pilote": "Pilote Lafayette — intégration API / flux métier avec chiffrage biométrique et filet de précision 0,08 mm.",
        "omega_atelier": "Atelier Omega — livrables multiples, délais serrés ou stack avancée ; devis sur mesure avec phasage.",
    }
    lines = [
        "Bonjour,",
        "",
        "Merci pour le détail de votre besoin. Côté **TryOnYou / Divineo**, nous travaillons avec une **précision de référence de "
        + precision_mm
        + " mm** (protocole Zero-Size) et une entité immatriculée en France (**SIREN "
        + siren
        + "**, patente "
        + patente
        + ").",
        "",
        "**Synthèse de votre demande :**",
        f"- Intention : {a.get('intent', '—')}",
        f"- Livrables détectés : {', '.join(a.get('deliverables') or ['—'])}",
        f"- Complexité estimée : {a.get('complexity', '—')}",
        "",
        "**Proposition de périmètre :**",
        f"- {tier_copy.get(tier, tier_copy['essai_zero_size'])}",
        "",
    ]
    if a.get("risk_flags"):
        lines.extend(
            [
                "**Points à clarifier avant devis fermé :**",
                *[f"- {r}" for r in a["risk_flags"]],
                "",
            ]
        )
    lines.extend(
        [
            "Je vous envoie un **devis technique chiffré** (phases + délais) dès validation de ces points ou après un court appel de cadrage.",
            "",
            "Cordialement,",
            "Rubén — TryOnYou / Divineo",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    import sys

    sample = sys.argv[1] if len(sys.argv) > 1 else (
        "Hi, I need a React app with 3D try-on and Shopify checkout in 2 weeks. Budget around $800."
    )
    out = analyze_client_message(sample)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print("---")
    print(draft_budget_proposal_technical(out))

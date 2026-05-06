"""
Resend-based brand outreach for TryOnYou pilot proposals.

Env vars:
    RESEND_API_KEY    – Resend secret key (re_...)
    RESEND_FROM_EMAIL – Verified sender (your Resend-verified address)
    RESEND_FROM_NAME  – Display name (default: Pau · TryOnYou)

Usage from Flask routes – see api/index.py wiring.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_RESEND_API_KEY: str = ""
_RESEND_FROM_EMAIL: str = ""
_RESEND_FROM_NAME: str = "Pau · TryOnYou"

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs" / "outreach"


def _env() -> tuple[str, str, str]:
    global _RESEND_API_KEY, _RESEND_FROM_EMAIL, _RESEND_FROM_NAME
    _RESEND_API_KEY = (os.getenv("RESEND_API_KEY") or "").strip()
    _RESEND_FROM_EMAIL = (os.getenv("RESEND_FROM_EMAIL") or "").strip()
    _RESEND_FROM_NAME = (os.getenv("RESEND_FROM_NAME") or "Pau · TryOnYou").strip()
    return _RESEND_API_KEY, _RESEND_FROM_EMAIL, _RESEND_FROM_NAME


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MASTER_BRAND_LIST: list[dict[str, str]] = [
    {"brand": "Balmain", "segment": "Haute Couture"},
    {"brand": "Dior", "segment": "Haute Couture"},
    {"brand": "Prada", "segment": "Luxury RTW"},
    {"brand": "Chanel", "segment": "Haute Couture"},
    {"brand": "Yves Saint Laurent", "segment": "Luxury RTW"},
    {"brand": "Givenchy", "segment": "Luxury RTW"},
    {"brand": "Valentino", "segment": "Luxury RTW"},
    {"brand": "Balenciaga", "segment": "Luxury RTW"},
    {"brand": "Loewe", "segment": "Luxury RTW"},
    {"brand": "Celine", "segment": "Luxury RTW"},
    {"brand": "Hermès", "segment": "Luxury RTW"},
    {"brand": "Louis Vuitton", "segment": "Luxury RTW"},
    {"brand": "Bottega Veneta", "segment": "Luxury RTW"},
    {"brand": "Fendi", "segment": "Luxury RTW"},
    {"brand": "Miu Miu", "segment": "Luxury RTW"},
    {"brand": "Alexander McQueen", "segment": "Luxury RTW"},
    {"brand": "Gucci", "segment": "Luxury RTW"},
    {"brand": "Burberry", "segment": "Luxury RTW"},
    {"brand": "Versace", "segment": "Luxury RTW"},
    {"brand": "Dolce & Gabbana", "segment": "Luxury RTW"},
    {"brand": "Etro", "segment": "Premium"},
    {"brand": "Max Mara", "segment": "Premium"},
    {"brand": "Brunello Cucinelli", "segment": "Premium"},
    {"brand": "Loro Piana", "segment": "Premium"},
    {"brand": "Zegna", "segment": "Premium"},
    {"brand": "Tom Ford", "segment": "Luxury RTW"},
    {"brand": "Stella McCartney", "segment": "Premium"},
    {"brand": "Isabel Marant", "segment": "Premium"},
    {"brand": "Jacquemus", "segment": "Premium"},
    {"brand": "Ami Paris", "segment": "Premium"},
    {"brand": "Kenzo", "segment": "Premium"},
    {"brand": "Sandro", "segment": "Contemporary"},
    {"brand": "Maje", "segment": "Contemporary"},
    {"brand": "Claudie Pierlot", "segment": "Contemporary"},
    {"brand": "Ba&sh", "segment": "Contemporary"},
    {"brand": "Zadig & Voltaire", "segment": "Contemporary"},
    {"brand": "The Kooples", "segment": "Contemporary"},
    {"brand": "IRO Paris", "segment": "Contemporary"},
    {"brand": "Maison Kitsuné", "segment": "Contemporary"},
    {"brand": "A.P.C.", "segment": "Contemporary"},
    {"brand": "Acne Studios", "segment": "Contemporary"},
    {"brand": "COS", "segment": "Contemporary"},
    {"brand": "& Other Stories", "segment": "Contemporary"},
    {"brand": "Massimo Dutti", "segment": "Contemporary"},
    {"brand": "Reiss", "segment": "Contemporary"},
    {"brand": "Hugo Boss", "segment": "Premium"},
    {"brand": "Karl Lagerfeld", "segment": "Contemporary"},
    {"brand": "Paul Smith", "segment": "Premium"},
    {"brand": "Lanvin", "segment": "Luxury RTW"},
    {"brand": "Boucheron", "segment": "Haute Joaillerie"},
    {"brand": "Cartier", "segment": "Haute Joaillerie"},
    {"brand": "Van Cleef & Arpels", "segment": "Haute Joaillerie"},
    {"brand": "Messika", "segment": "Fine Jewellery"},
    {"brand": "Piaget", "segment": "Haute Joaillerie"},
    {"brand": "Chaumet", "segment": "Fine Jewellery"},
    {"brand": "Moncler", "segment": "Luxury RTW"},
    {"brand": "Canada Goose", "segment": "Premium"},
    {"brand": "Stone Island", "segment": "Premium"},
    {"brand": "Off-White", "segment": "Luxury RTW"},
    {"brand": "Maison Margiela", "segment": "Luxury RTW"},
    {"brand": "Rick Owens", "segment": "Luxury RTW"},
]


def _build_html(brand_name: str, segment: str, lang: str = "en") -> str:
    if lang == "fr":
        return f"""\
<div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <h1 style="font-size:22px;color:#D4AF37;margin-bottom:4px">TryOnYou × {brand_name}</h1>
  <p style="font-size:13px;color:#888;margin-top:0">{segment} · Pilote Galeries Lafayette</p>
  <hr style="border:none;border-top:1px solid #D4AF37;margin:16px 0">
  <p>Bonjour,</p>
  <p>Nous avons développé un <strong>miroir digital souverain</strong> qui élimine
  l'incertitude de la taille — sans afficher de mensurations, sans complexes.</p>
  <ul style="padding-left:18px;line-height:1.7">
    <li><strong>Résultat pilote :</strong> réduction de 30 % des retours logistiques.</li>
    <li><strong>Expérience :</strong> scan corporel invisible (zéro chiffre affiché au client).</li>
    <li><strong>Technologie :</strong> brevetée (PCT/EP2025/067317), déployée chez Lafayette Haussmann.</li>
  </ul>
  <p>Seriez-vous disponible cette semaine pour une démo de 15 minutes ?</p>
  <p style="margin-top:24px">Cordialement,<br>
  <strong>Pau</strong> — Personal AI Stylist<br>
  <span style="color:#888">TryOnYou · Maison Digitale · Paris</span></p>
</div>"""

    if lang == "es":
        return f"""\
<div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <h1 style="font-size:22px;color:#D4AF37;margin-bottom:4px">TryOnYou × {brand_name}</h1>
  <p style="font-size:13px;color:#888;margin-top:0">{segment} · Piloto Galeries Lafayette</p>
  <hr style="border:none;border-top:1px solid #D4AF37;margin:16px 0">
  <p>Buenos días,</p>
  <p>Hemos desarrollado un <strong>espejo digital soberano</strong> que elimina
  la incertidumbre de la talla — sin mostrar medidas, sin complejos.</p>
  <ul style="padding-left:18px;line-height:1.7">
    <li><strong>Resultado piloto:</strong> reducción del 30 % en devoluciones logísticas.</li>
    <li><strong>Experiencia:</strong> escaneo corporal invisible (cero cifras visibles al cliente).</li>
    <li><strong>Tecnología:</strong> patentada (PCT/EP2025/067317), desplegada en Lafayette Haussmann.</li>
  </ul>
  <p>¿Tendría disponibilidad esta semana para una demo de 15 minutos?</p>
  <p style="margin-top:24px">Un saludo,<br>
  <strong>Pau</strong> — Personal AI Stylist<br>
  <span style="color:#888">TryOnYou · Maison Digitale · París</span></p>
</div>"""

    return f"""\
<div style="font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;max-width:600px;margin:0 auto;color:#1a1a1a">
  <h1 style="font-size:22px;color:#D4AF37;margin-bottom:4px">TryOnYou × {brand_name}</h1>
  <p style="font-size:13px;color:#888;margin-top:0">{segment} · Galeries Lafayette Pilot</p>
  <hr style="border:none;border-top:1px solid #D4AF37;margin:16px 0">
  <p>Hello,</p>
  <p>We've built a <strong>sovereign digital mirror</strong> that eliminates
  sizing uncertainty — no measurements shown, no body-shaming.</p>
  <ul style="padding-left:18px;line-height:1.7">
    <li><strong>Pilot result:</strong> 30 % reduction in logistics returns.</li>
    <li><strong>Experience:</strong> invisible body scan (zero numbers displayed to the customer).</li>
    <li><strong>Technology:</strong> patented (PCT/EP2025/067317), deployed at Lafayette Haussmann.</li>
  </ul>
  <p>Would you be available this week for a 15-minute demo?</p>
  <p style="margin-top:24px">Best regards,<br>
  <strong>Pau</strong> — Personal AI Stylist<br>
  <span style="color:#888">TryOnYou · Maison Digitale · Paris</span></p>
</div>"""


def _subject(brand_name: str, lang: str = "en") -> str:
    if lang == "fr":
        return f"Miroir Digital : stratégie 0 % retours pour {brand_name}"
    if lang == "es":
        return f"Espejo Digital: estrategia 0 % devoluciones para {brand_name}"
    return f"Digital Mirror Pilot: 0% Returns Strategy for {brand_name}"


def _log_send(brand: str, email: str, status: str, detail: str = "") -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "brand": brand,
        "email": email,
        "status": status,
        "detail": detail,
    }
    log_path = _LOG_DIR / f"outreach_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def is_outreach_configured() -> bool:
    api_key, from_email, _ = _env()
    return bool(api_key) and bool(from_email)


def send_brand_proposal(
    brand_name: str,
    contact_email: str,
    lang: str = "en",
    segment: str = "Luxury RTW",
) -> dict[str, Any]:
    """Send a single brand proposal via Resend. Returns a result dict."""
    api_key, from_email, from_name = _env()

    if not api_key:
        return {"ok": False, "error": "RESEND_API_KEY not configured"}
    if not from_email:
        return {"ok": False, "error": "RESEND_FROM_EMAIL not configured"}
    if not _EMAIL_RE.match(contact_email):
        return {"ok": False, "error": f"invalid recipient email: {contact_email}"}

    lang = lang if lang in ("fr", "en", "es") else "en"

    try:
        import resend as _resend

        _resend.api_key = api_key
        params: dict[str, Any] = {
            "from": f"{from_name} <{from_email}>",
            "to": [contact_email],
            "subject": _subject(brand_name, lang),
            "html": _build_html(brand_name, segment, lang),
        }
        result = _resend.Emails.send(params)
        _log_send(brand_name, contact_email, "sent", json.dumps(result, default=str))
        return {"ok": True, "resend_id": result.get("id") if isinstance(result, dict) else str(result)}
    except ImportError:
        _log_send(brand_name, contact_email, "error", "resend package not installed")
        return {"ok": False, "error": "resend package not installed (pip install resend)"}
    except Exception as exc:
        _log_send(brand_name, contact_email, "error", str(exc))
        return {"ok": False, "error": str(exc)}


def send_batch_proposals(
    targets: list[dict[str, str]],
    lang: str = "en",
) -> dict[str, Any]:
    """
    Send proposals to a batch of brands.

    Each item in *targets* must have at least ``email`` and ``brand``;
    ``segment`` is optional (defaults to the master list match or "Luxury RTW").
    """
    results: list[dict[str, Any]] = []
    sent = 0
    errors = 0

    brand_segment_map = {b["brand"].lower(): b["segment"] for b in MASTER_BRAND_LIST}

    for t in targets:
        email = (t.get("email") or "").strip()
        brand = (t.get("brand") or "").strip()
        segment = (t.get("segment") or brand_segment_map.get(brand.lower(), "Luxury RTW")).strip()

        if not email or not brand:
            results.append({"brand": brand, "email": email, "ok": False, "error": "missing brand or email"})
            errors += 1
            continue

        r = send_brand_proposal(brand, email, lang=lang, segment=segment)
        r["brand"] = brand
        r["email"] = email
        results.append(r)
        if r["ok"]:
            sent += 1
        else:
            errors += 1

    return {
        "total": len(targets),
        "sent": sent,
        "errors": errors,
        "results": results,
    }


def get_brand_list() -> list[dict[str, str]]:
    return [dict(b) for b in MASTER_BRAND_LIST]


def get_outreach_logs(limit: int = 50) -> list[dict[str, Any]]:
    """Return the most recent outreach log entries."""
    entries: list[dict[str, Any]] = []
    if not _LOG_DIR.exists():
        return entries
    log_files = sorted(_LOG_DIR.glob("outreach_*.jsonl"), reverse=True)
    for lf in log_files:
        with open(lf, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
                if len(entries) >= limit:
                    break
        if len(entries) >= limit:
            break
    return entries[:limit]

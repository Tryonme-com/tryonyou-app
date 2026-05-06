"""
Brand Outreach Campaign — Resend-based email campaign for 60 luxury fashion brands.
Uses the Resend API (https://resend.com) for transactional email delivery.
Tracks campaign status, bounce handling, and per-brand personalization.

Environment:
    RESEND_API_KEY          — Resend secret key (re_...)
    CAMPAIGN_FROM_EMAIL     — Sender address configured per deployment
    CAMPAIGN_FROM_NAME      — Sender display name (default: "Pau · TryOnYou")
    CAMPAIGN_DEMO_VIDEO_URL — Link to the demo video (Vimeo/Drive)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

_RESEND_API_URL = "https://api.resend.com/emails"
_LOG_PATH = Path("/tmp/brand_outreach_log.jsonl")

BRANDS_60 = [
    "LVMH", "Kering", "Inditex", "Prada Group", "Burberry",
    "Hermès", "Chanel", "Richemont", "Tapestry", "Capri Holdings",
    "Moncler", "Salvatore Ferragamo", "Tod's", "Hugo Boss", "Max Mara",
    "Valentino", "Dolce & Gabbana", "Armani", "Versace", "Balenciaga",
    "Givenchy", "Fendi", "Loewe", "Celine", "Bottega Veneta",
    "Saint Laurent", "Alexander McQueen", "Stella McCartney", "Marni", "Jil Sander",
    "Zegna", "Brunello Cucinelli", "Etro", "Missoni", "Loro Piana",
    "Miu Miu", "Balmain", "Lanvin", "Rochas", "Courrèges",
    "Sandro", "Maje", "Isabel Marant", "The Kooples", "AMI Paris",
    "Jacquemus", "Coperni", "Marine Serre", "Mugler", "Rabanne",
    "Dries Van Noten", "Maison Margiela", "Rick Owens", "Off-White", "Palm Angels",
    "Stone Island", "C.P. Company", "Diesel", "Marella", "Elisabetta Franchi",
]


def _get_resend_key() -> str:
    return (os.getenv("RESEND_API_KEY") or "").strip()


def _get_sender() -> str:
    name = os.getenv("CAMPAIGN_FROM_NAME", "Pau · TryOnYou")
    email = os.getenv("CAMPAIGN_FROM_EMAIL", "pau@tryonme.app")
    return f"{name} <{email}>"


def _get_demo_video_url() -> str:
    return os.getenv("CAMPAIGN_DEMO_VIDEO_URL", "https://tryonme.app/demo")


def _build_email_html(brand_name: str) -> str:
    video_url = _get_demo_video_url()
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"></head>
<body style="font-family:'Helvetica Neue',Arial,sans-serif;color:#1a1a1a;max-width:600px;margin:0 auto;padding:32px;">
  <div style="border-bottom:2px solid #D4AF37;padding-bottom:16px;margin-bottom:24px;">
    <h1 style="font-size:22px;margin:0;">Digital Mirror Pilot: 0% Returns Strategy</h1>
    <p style="color:#666;margin:4px 0 0;">Exclusively for <strong>{brand_name}</strong></p>
  </div>
  <p>We have developed a biometric algorithm that eliminates size uncertainty for your customers — <strong>reducing logistics returns by up to 30%</strong>.</p>
  <ul style="line-height:1.8;">
    <li><strong>Key Metric:</strong> 30% reduction in size-related returns (pilot data, Galeries Lafayette Haussmann).</li>
    <li><strong>Experience:</strong> Invisible body scan — no numbers, no complexes. The customer sees the fit before paying.</li>
    <li><strong>Technology:</strong> Patent PCT/EP2025/067317 — sovereign biometric engine, GDPR-compliant, zero data storage.</li>
  </ul>
  <p style="margin-top:24px;">
    <a href="{video_url}" style="display:inline-block;background:#D4AF37;color:#141619;padding:12px 24px;text-decoration:none;font-weight:bold;border-radius:4px;">Watch the Demo →</a>
  </p>
  <p style="margin-top:24px;color:#555;">Shall we schedule a 15-minute call this week?</p>
  <hr style="border:none;border-top:1px solid #eee;margin:32px 0 16px;">
  <p style="font-size:12px;color:#999;">
    TryOnYou · Maison Digitale · Paris<br>
    SIRET 94361019600017 · Patent PCT/EP2025/067317
  </p>
</body>
</html>"""


def _log_event(event: dict):
    event["timestamp"] = datetime.now(timezone.utc).isoformat()
    with open(_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def send_brand_email(brand_name: str, recipient_email: str, subject: str | None = None) -> dict:
    """Send a personalized outreach email to a single brand contact via Resend API."""
    api_key = _get_resend_key()
    if not api_key:
        return {"ok": False, "error": "RESEND_API_KEY not configured"}

    final_subject = subject or f"Digital Mirror Pilot: 0% Returns Strategy for {brand_name}"

    payload = {
        "from": _get_sender(),
        "to": [recipient_email],
        "subject": final_subject,
        "html": _build_email_html(brand_name),
        "tags": [
            {"name": "campaign", "value": "brand_outreach_v1"},
            {"name": "brand", "value": brand_name.lower().replace(" ", "_")},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(_RESEND_API_URL, json=payload, headers=headers, timeout=15)
        result = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"raw": resp.text}
        success = resp.status_code in (200, 201)

        _log_event({
            "action": "send",
            "brand": brand_name,
            "to": recipient_email,
            "status": "sent" if success else "failed",
            "resend_id": result.get("id"),
            "http_status": resp.status_code,
        })

        return {"ok": success, "brand": brand_name, "to": recipient_email, "resend_response": result}

    except Exception as exc:
        _log_event({"action": "send", "brand": brand_name, "to": recipient_email, "status": "error", "error": str(exc)})
        return {"ok": False, "brand": brand_name, "error": str(exc)}


def _infer_contact_email(brand_name: str) -> str:
    """Infer a generic innovation contact email from brand name."""
    slug = brand_name.lower().replace(" ", "").replace("&", "and").replace("'", "").replace("è", "e")
    return f"innovation@{slug}.com"


def execute_campaign(brands: list[str] | None = None, custom_contacts: dict | None = None) -> dict:
    """
    Run the full outreach campaign for the given brands (default: all 60).
    custom_contacts: optional {brand_name: email} overrides.
    """
    targets = brands or BRANDS_60
    contacts = custom_contacts or {}
    results = {"sent": 0, "failed": 0, "errors": [], "details": []}

    for brand in targets:
        email = contacts.get(brand) or _infer_contact_email(brand)
        outcome = send_brand_email(brand, email)
        results["details"].append(outcome)
        if outcome.get("ok"):
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({"brand": brand, "error": outcome.get("error") or outcome.get("resend_response")})

    results["total"] = len(targets)
    results["campaign_id"] = f"OUTREACH-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    _log_event({"action": "campaign_complete", "campaign_id": results["campaign_id"], "sent": results["sent"], "failed": results["failed"]})
    return results


def get_campaign_log() -> list[dict]:
    """Read the campaign log entries."""
    if not _LOG_PATH.exists():
        return []
    entries = []
    with open(_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def get_campaign_status() -> dict:
    """Summary of campaign activity."""
    log = get_campaign_log()
    sent = sum(1 for e in log if e.get("action") == "send" and e.get("status") == "sent")
    failed = sum(1 for e in log if e.get("action") == "send" and e.get("status") in ("failed", "error"))
    return {
        "configured": bool(_get_resend_key()),
        "total_brands": len(BRANDS_60),
        "emails_sent": sent,
        "emails_failed": failed,
        "log_entries": len(log),
    }


def get_brands_list() -> list[dict]:
    """Return full brands list with inferred contact emails."""
    return [{"name": b, "contact_email": _infer_contact_email(b)} for b in BRANDS_60]

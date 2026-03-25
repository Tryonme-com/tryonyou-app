"""
Mirror Sanctuary V10 Omega — Jules Backend
Patente PCT/EP2025/067317
Protocolo: V10.4_Lafayette
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


# ── Helpers ────────────────────────────────────────────────────────────────

def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _stripe_links() -> tuple[str, str]:
    """Resolve Stripe payment links from environment variables."""
    link_45 = (
        os.environ.get("STRIPE_LINK_SOVEREIGNTY_4_5M", "").strip()
        or os.environ.get("VITE_STRIPE_LINK_SOVEREIGNTY_4_5M", "").strip()
        or os.environ.get("STRIPE_LINK_4_5M_EUR", "").strip()
    )
    link_98 = (
        os.environ.get("STRIPE_LINK_SOVEREIGNTY_98K", "").strip()
        or os.environ.get("VITE_STRIPE_LINK_SOVEREIGNTY_98K", "").strip()
        or os.environ.get("STRIPE_LINK_98K_EUR", "").strip()
    )
    return (link_45 or "#", link_98 or "#")


def _stripe_configured() -> bool:
    """Return True if at least one Stripe link is configured."""
    a, b = _stripe_links()
    return a != "#" or b != "#"


def _html_index_body() -> bytes | None:
    """Load and inject Stripe links into the HTML template."""
    root = _project_root()
    link_45, link_98 = _stripe_links()
    candidates = [
        "index.html",
        os.path.join("src", "templates", "mirror_v10_final.html"),
    ]
    for rel in candidates:
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                html = f.read()
            html = (
                html.replace("{{STRIPE_LINK_4_5M}}", link_45)
                    .replace("{{STRIPE_LINK_98K}}", link_98)
            )
            return html.encode("utf-8")
    return None


def _send_json(handler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.end_headers()
    handler.wfile.write(body)


def _send_html(handler, html_bytes: bytes) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(html_bytes)))
    handler.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    handler.end_headers()
    handler.wfile.write(html_bytes)


def _serve_file(
    handler,
    rel_path: str,
    content_type: str,
    cache: str = "public, max-age=86400",
) -> None:
    """Serve a static file with path traversal protection."""
    root = _project_root()
    filepath = os.path.normpath(os.path.join(root, rel_path))
    # Path traversal guard
    if not filepath.startswith(os.path.normpath(root + os.sep)):
        _send_json(handler, 403, {"error": "Forbidden"})
        return
    if not os.path.isfile(filepath):
        _send_json(handler, 404, {"error": f"{rel_path} not found"})
        return
    with open(filepath, "rb") as f:
        data = f.read()
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Cache-Control", cache)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Accept-Ranges", "bytes")
    handler.end_headers()
    handler.wfile.write(data)


def _read_body(handler) -> bytes:
    """Read request body safely."""
    try:
        length = int(handler.headers.get("Content-Length", 0))
        return handler.rfile.read(length) if length > 0 else b""
    except (ValueError, OSError):
        return b""


# ── Request Handler ────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):  # noqa: A002
        """Suppress default HTTP logging to keep Vercel logs clean."""
        pass

    # ── OPTIONS (CORS preflight) ──
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Stripe-Signature")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ── POST ──
    def do_POST(self):
        path = urlparse(self.path).path

        # ── Stripe Webhook ──
        if path == "/api/webhook":
            self._handle_stripe_webhook()
            return

        # ── Jules API ──
        link_45, link_98 = _stripe_links()
        response = {
            "status": "DIVINEO_ACTIVE",
            "version": "V10.4_Lafayette",
            "patente": "PCT/EP2025/067317",
            "jules_msg": (
                "Bonjour, c'est Jules. Recibido. "
                "El arquitecto está validando su precisión. "
                "Hablamos en un 'snap'."
            ),
            "protocolo": "Mirror Sanctuary Omega",
            "next_step": "A fuego!",
            "stripe_configured": _stripe_configured(),
            "stripe_link_sovereignty_4_5m_eur": link_45 if link_45 != "#" else None,
            "stripe_link_sovereignty_98k_eur": link_98 if link_98 != "#" else None,
        }
        _send_json(self, 200, response)

    def _handle_stripe_webhook(self):
        """
        Stripe webhook endpoint.
        Verifies the Stripe-Signature header when STRIPE_WEBHOOK_SECRET is set.
        Handles checkout.session.completed events.
        """
        body = _read_body(self)
        sig_header = self.headers.get("Stripe-Signature", "")
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()

        # Signature verification (only when secret is configured)
        if webhook_secret and sig_header:
            try:
                import hmac
                import hashlib
                import time as _time

                # Parse Stripe signature header: t=...,v1=...
                parts = dict(item.split("=", 1) for item in sig_header.split(",") if "=" in item)
                timestamp = parts.get("t", "")
                signature = parts.get("v1", "")

                # Replay attack protection: reject events older than 5 minutes
                try:
                    ts = int(timestamp)
                    if abs(_time.time() - ts) > 300:
                        _send_json(self, 400, {"error": "Webhook timestamp too old"})
                        return
                except ValueError:
                    _send_json(self, 400, {"error": "Invalid timestamp"})
                    return

                signed_payload = f"{timestamp}.".encode() + body
                expected = hmac.new(
                    webhook_secret.encode("utf-8"),
                    signed_payload,
                    hashlib.sha256,
                ).hexdigest()

                if not hmac.compare_digest(expected, signature):
                    _send_json(self, 400, {"error": "Invalid signature"})
                    return
            except Exception:
                _send_json(self, 400, {"error": "Signature verification failed"})
                return

        # Parse event
        try:
            event = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            _send_json(self, 400, {"error": "Invalid JSON payload"})
            return

        event_type = event.get("type", "")

        # Handle checkout.session.completed
        if event_type == "checkout.session.completed":
            session = event.get("data", {}).get("object", {})
            amount_total = session.get("amount_total", 0)
            currency = session.get("currency", "eur").upper()
            customer_email = session.get("customer_details", {}).get("email", "")
            session_id = session.get("id", "")

            # Log the confirmed payment (Vercel function logs)
            print(
                f"[Jules] PAGO CONFIRMADO — "
                f"Session: {session_id} | "
                f"Importe: {amount_total / 100:.2f} {currency} | "
                f"Cliente: {customer_email or 'N/A'}"
            )

            _send_json(self, 200, {
                "received": True,
                "event": event_type,
                "session_id": session_id,
                "amount": amount_total,
                "currency": currency,
                "jules_msg": "Pago confirmado. Protocolo Soberanía activado.",
            })
            return

        # Acknowledge all other events
        _send_json(self, 200, {"received": True, "event": event_type})

    # ── GET ──
    def do_GET(self):
        path = urlparse(self.path).path

        # ── Health check ──
        if path == "/api/health":
            link_45, link_98 = _stripe_links()
            _send_json(self, 200, {
                "status": "ok",
                "version": "V10.4_Lafayette",
                "patente": "PCT/EP2025/067317",
                "stripe_configured": _stripe_configured(),
                "stripe_4_5m_set": link_45 != "#",
                "stripe_98k_set": link_98 != "#",
                "webhook_secret_set": bool(os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()),
            })
            return

        # ── Static assets ──
        if path == "/hero.mp4":
            _serve_file(self, "hero.mp4", "video/mp4", "public, max-age=604800")
            return

        if path == "/lafayette_collection.json":
            _serve_file(
                self,
                os.path.join("src", "data", "lafayette_collection.json"),
                "application/json; charset=utf-8",
                "public, max-age=3600",
            )
            return

        if path == "/logo_pavo_real.png":
            _serve_file(self, "logo_pavo_real.png", "image/png")
            return

        # ── Main HTML ──
        html_body = _html_index_body()
        if html_body is not None:
            _send_html(self, html_body)
            return

        # ── Fallback ──
        plain = (
            "Mirror Sanctuary V10 Omega — Búnker 75005 Operativo. "
            "tryonyou-app V10.4 Online. "
            "Patente PCT/EP2025/067317."
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(plain)))
        self.end_headers()
        self.wfile.write(plain)

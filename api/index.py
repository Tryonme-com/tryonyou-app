"""
TryOnYou — Jules V10 Omega (Vercel serverless, Pure SPA + bridges).

- GET: SPA (dist/index.html tras npm run build), estáticos, santuario V10.
- POST: handshake Jules, leads Zero-Size, biometría (firewall émotionnel),
  checkout « sélection parfaite » (Shopify + Amazon, sans tailles).
- ANTI-ACCUMULATION: una talla certificada por trayectoria; metadatos `anti_accumulation`
  / `single_size_certitude` en checkout y snap (ver MISSION.md).
- Campos estables para Make.com: intent, lead_id, timestamp_iso, siren, patente, protocol.
- Webhook opcional: TRYONYOU_LEAD_WEBHOOK_URL (o MAKE_LEADS_WEBHOOK_URL / MAKE_WEBHOOK_URL);
  cuerpo JSON: { "event": "tryonyou_lead_v1", ...mismo payload HTTP }.
- Integración Peacock_Core: prohibido destino webhook hacia abvetos.com; licencia activada sólo en proceso interno manual.

CLI local: python3 api/index.py --action send_bpifrance_emergency
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

_API_DIR = os.path.dirname(os.path.abspath(__file__))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from peacock_core import is_webhook_destination_forbidden
from stealth_bunker import (
    append_sistema_suspendido_log,
    bunker_blackout_mode,
    bunker_stealth_enabled,
    client_ip,
    inventory_collection_path_forbidden,
    inventory_references_unlocked,
    lafayette_ip_matches,
    log_bunker_access,
    maybe_log_ttc_unlock_event,
    stealth_html_body,
)

_STATIC_EXTS: frozenset[str] = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".svg",
        ".ico",
        ".webm",
        ".mp4",
        ".mp3",
        ".js",
        ".css",
        ".json",
        ".woff2",
        ".txt",
        ".map",
    }
)

_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".mp3": "audio/mpeg",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8",
    ".map": "application/json; charset=utf-8",
}

SIREN_SELL = "943 610 196"
PATENTE = "PCT/EP2025/067317"
PRODUCT_LANE = "tryonyou_v10_omega"

_VALID_INTENTS = frozenset({"selection", "reserve", "combo", "save", "share"})


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _slack_notify(text: str) -> None:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        return
    if is_webhook_destination_forbidden(url):
        return
    payload = json.dumps({"text": text[:3500]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            del r
    except (urllib.error.URLError, TimeoutError, OSError):
        return


def _lead_webhook_url() -> str:
    """Webhooks dedicado a leads (recomendado); si no, MAKE_WEBHOOK_URL."""
    return (
        os.environ.get("TRYONYOU_LEAD_WEBHOOK_URL", "").strip()
        or os.environ.get("MAKE_LEADS_WEBHOOK_URL", "").strip()
        or os.environ.get("MAKE_WEBHOOK_URL", "").strip()
    )


def _make_forward_lead(payload: dict) -> None:
    """Encadena Make.com sin bloquear la respuesta al cliente (mismos campos que el JSON HTTP)."""
    url = _lead_webhook_url()
    if not url:
        return
    if is_webhook_destination_forbidden(url):
        return
    envelope = {
        "event": "tryonyou_lead_v1",
        **payload,
    }
    body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            del r
    except (urllib.error.URLError, TimeoutError, OSError):
        return


def _stripe_links() -> tuple[str, str]:
    a = (
        os.environ.get("STRIPE_LINK_SOVEREIGNTY_4_5M", "").strip()
        or os.environ.get("VITE_STRIPE_LINK_SOVEREIGNTY_4_5M", "").strip()
        or os.environ.get("STRIPE_LINK_4_5M_EUR", "").strip()
    )
    b = (
        os.environ.get("STRIPE_LINK_SOVEREIGNTY_98K", "").strip()
        or os.environ.get("VITE_STRIPE_LINK_SOVEREIGNTY_98K", "").strip()
        or os.environ.get("STRIPE_LINK_98K_EUR", "").strip()
    )
    return (a or "#", b or "#")


def _inject_stripe(html: str) -> str:
    link_45, link_98 = _stripe_links()
    return (
                html.replace("{{STRIPE_LINK_4_5M}}", link_45)
                .replace("{{STRIPE_LINK_98K}}", link_98)
            )


def _html_index_body() -> bytes | None:
    """
    SOLO dist/index.html (bundle Vite con /assets/*). Nunca el index.html raíz
    que referencia /src/main.tsx — eso en producción muestra landings rotos o estáticos ajenos.

    BUNKER_STEALTH_TOTAL: cocotte SACMUSEUM (no SPA) vía stealth_html_body().
    """
    if bunker_stealth_enabled():
        return stealth_html_body()
    root = _project_root()
    dist_index = os.path.join(root, "dist", "index.html")
    if os.path.isfile(dist_index):
        with open(dist_index, encoding="utf-8") as f:
            html = _inject_stripe(f.read())
        return html.encode("utf-8")
    tmpl = os.path.join(root, "src", "templates", "mirror_v10_final.html")
    if os.path.isfile(tmpl):
        with open(tmpl, encoding="utf-8") as f:
            html = _inject_stripe(f.read())
            return html.encode("utf-8")
    msg = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>TRYONYOU V10</title></head>"
        "<body style='font-family:sans-serif;background:#141619;color:#C5A46D;padding:2rem'>"
        "<p>Build SPA ausente — ejecutar <code>npm run build</code> en despliegue.</p>"
        "<p>Patente PCT/EP2025/067317 · SIREN 943 610 196</p></body></html>"
    )
    return msg.encode("utf-8")


def _resolve_safe_static(url_path: str) -> str | None:
    root = _project_root()
    root_prefix = os.path.normpath(root + os.sep)
    path = url_path
    if path.startswith("/"):
        path = path[1:]
    if not path or path.endswith("/"):
        return None
    if inventory_collection_path_forbidden("/" + path):
        return None

    candidates = [
        os.path.normpath(os.path.join(root, path)),
        os.path.normpath(os.path.join(root, "dist", path)),
    ]
    for candidate in candidates:
        if not candidate.startswith(root_prefix):
            continue
        if not os.path.isfile(candidate):
            continue
        ext = os.path.splitext(candidate)[1].lower()
        if ext not in _STATIC_EXTS:
            continue
        rel = os.path.relpath(candidate, root)
        if rel.startswith("..") or os.path.isabs(rel):
            continue
        if rel == "index.html" or rel.endswith(os.sep + "index.html"):
            continue
        if rel.startswith(".git" + os.sep) or rel.startswith("api" + os.sep):
            continue
        return candidate
    return None


def _html_mirror_sanctuary() -> bytes | None:
    root = _project_root()
    p = os.path.join(root, "mirror_sanctuary_v10.html")
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8") as f:
        return f.read().encode("utf-8")


def _send_binary(handler: BaseHTTPRequestHandler, data: bytes, content_type: str) -> None:
    handler.send_response(200)
    handler.send_header("Content-type", content_type)
    handler.send_header("Cache-Control", "public, max-age=3600")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _send_json(handler: BaseHTTPRequestHandler, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _send_json_error(handler: BaseHTTPRequestHandler, code: int, msg: str) -> None:
    body = json.dumps({"ok": False, "error": msg, "siren": SIREN_SELL, "patente": PATENTE}).encode(
        "utf-8"
    )
    handler.send_response(code)
    handler.send_header("Content-type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _lead_db_path() -> str:
    """Divineo_Leads_DB: prioriza DIVINEO_LEADS_DB_PATH, luego LEADS_DB_PATH."""
    return (
        os.environ.get("DIVINEO_LEADS_DB_PATH", "").strip()
        or os.environ.get("LEADS_DB_PATH", "").strip()
        or "/tmp/Divineo_Leads_v10.db"
    )


def _ensure_leads_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            intent TEXT NOT NULL,
            source TEXT,
            contact_hint TEXT,
            meta_json TEXT
        )
        """
    )


def _perfect_checkout_urls(lead_id: int, fabric_sensation: str) -> tuple[str | None, str | None]:
    from amazon_bridge import resolve_amazon_checkout_url
    from shopify_bridge import resolve_shopify_checkout_url

    return (
        resolve_shopify_checkout_url(lead_id, fabric_sensation),
        resolve_amazon_checkout_url(lead_id, fabric_sensation),
    )


def _insert_lead(
    intent: str,
    source: str,
    contact_hint: str | None,
    meta: dict,
) -> tuple[int, str]:
    ts = datetime.now(timezone.utc).isoformat()
    meta_json = json.dumps(meta, ensure_ascii=False)
    conn = sqlite3.connect(_lead_db_path(), check_same_thread=False)
    try:
        _ensure_leads_table(conn)
        cur = conn.execute(
            "INSERT INTO leads (created_at, intent, source, contact_hint, meta_json) VALUES (?,?,?,?,?)",
            (ts, intent, source, contact_hint or "", meta_json),
        )
        conn.commit()
        return int(cur.lastrowid or 0), ts
    finally:
        conn.close()


def _jules_payload() -> dict:
    link_45, link_98 = _stripe_links()
    return {
        "status": "DIVINEO_ACTIVE",
        "jules_msg": (
            "Bonjour — Jules. Protocole Zero-Size actif. "
            "L'orchestration Rubén Espinar Rodríguez / Divineo valide la précision. "
            "On se parle au prochain snap."
        ),
        "protocolo": "V10.4_Lafayette",
        "next_step": "A fuego!",
        "patente": PATENTE,
        "siren": SIREN_SELL,
        "product_lane": PRODUCT_LANE,
        "stripe_link_sovereignty_4_5m_eur": link_45 if link_45 != "#" else "",
        "stripe_link_sovereignty_98k_eur": link_98 if link_98 != "#" else "",
    }


def _inventory_kill_paths_block(method: str, path_key: str) -> bool:
    if inventory_references_unlocked():
        return False
    if method == "GET" and path_key == "/api/v1/inventory/status":
        return True
    if method == "POST" and path_key in (
        "/api/v1/inventory/match",
        "/api/v1/mirror/snap",
    ):
        return True
    return False


_SLACK_SUSPENDIDO_SENT = False


def _maybe_slack_sistema_suspendido() -> None:
    global _SLACK_SUSPENDIDO_SENT
    if _SLACK_SUSPENDIDO_SENT:
        return
    if not bunker_blackout_mode():
        return
    _SLACK_SUSPENDIDO_SENT = True
    _slack_notify(
        "TryOnYou · Sistema Suspendido — blackout Lafayette / 9 000 € TTC non confirmé. "
        f"{PATENTE} · SIREN {SIREN_SELL}"
    )


def _respond_inventory_locked(
    handler: BaseHTTPRequestHandler, path_key: str, method: str
) -> None:
    code = 403
    outcome = "inventory_locked"
    detail = "setup_9000_ttc_not_validated"
    msg = (
        "Inventaire verrouillé — validation du règlement 9 000 € TTC "
        "(facture F-2026-001) requise."
    )
    if bunker_blackout_mode() and lafayette_ip_matches(handler):
        code = 503
        outcome = "service_unavailable_blackout"
        detail = "lafayette_9k_pending"
        msg = (
            "Service Unavailable — moteur V10 suspendu (abono 9 000 € TTC). "
            "Réessayer après validation."
        )
    log_bunker_access(handler, method, path_key, outcome, detail, code)
    if bunker_blackout_mode() and code == 503:
        append_sistema_suspendido_log(client_ip(handler), detail)
        _maybe_slack_sistema_suspendido()
    _send_json_error(handler, code, msg)


def _stealth_should_log(method: str, path_key: str) -> bool:
    if path_key.startswith("/api"):
        return True
    if path_key in ("/", "/index.html"):
        return True
    if path_key in ("/mirror_sanctuary_v10.html", "/mirror_sanctuary_v10"):
        return True
    return False


class handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        if _inventory_kill_paths_block("POST", path):
            _respond_inventory_locked(self, path, "POST")
            return
        try:
            body_json = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            _send_json_error(self, 400, "JSON invalide")
            return

        if bunker_stealth_enabled() and _stealth_should_log("POST", path):
            log_bunker_access(self, "POST", path, "request", "", 200)

        if path in ("/api/v1/leads",):
            intent = str(body_json.get("intent", "")).strip().lower()
            if intent not in _VALID_INTENTS:
                _send_json_error(
                    self,
                    400,
                    "intent requis: selection|reserve|combo|save|share",
                )
                return
            source = str(body_json.get("source", "ofrenda_v10"))[:128]
            contact = body_json.get("contact_hint")
            contact_s = str(contact).strip()[:320] if contact else None
            meta = {
                "protocol": str(body_json.get("protocol", "zero_size"))[:64],
                "extras": body_json.get("extras") if isinstance(body_json.get("extras"), dict) else {},
            }
            try:
                lead_id, ts = _insert_lead(intent, source, contact_s, meta)
            except OSError:
                lead_id, ts = 0, datetime.now(timezone.utc).isoformat()

            payload = {
                "ok": True,
                "lead_id": lead_id,
                "timestamp_iso": ts,
                "intent": intent,
                "source": source,
                "siren": SIREN_SELL,
                "patente": PATENTE,
                "product_lane": PRODUCT_LANE,
                "protocol": "zero_size",
            }
            _slack_notify(
                f"TryOnYou · lead {intent} · id {lead_id} · {PATENTE} · SIREN {SIREN_SELL}"
            )
            _make_forward_lead(payload)
            _send_json(self, payload)
            return

        if path in ("/api/v1/biometrics",):
            feats = body_json.get("features")
            if not isinstance(feats, list) or len(feats) < 4:
                _send_json_error(self, 400, "features: liste numérique (min 4 valeurs, anonymisées)")
                return
            session_id = str(body_json.get("session_id", "anon"))[:128]
            try:
                vals = [float(x) for x in feats[:64]]
            except (TypeError, ValueError):
                _send_json_error(self, 400, "features: nombres invalides")
                return
            center = sum(vals) / len(vals)
            elasticity = max(0.0, min(1.0, 0.5 + 0.45 * math.tanh(center)))
            verdict = "aligned"
            if elasticity < 0.35:
                verdict = "drape_bias"
            elif elasticity > 0.72:
                verdict = "tension_bias"
            emotional = {
                "aligned": "Fluidité noble — le drapé épouse votre ligne sans friction.",
                "drape_bias": "Préférence pour le tombe — élégance détendue, ajustage souverain.",
                "tension_bias": "Structure affirmée — tenue précise, silhouette sculptée.",
            }
            _send_json(
                self,
                {
                    "ok": True,
                    "session_id": session_id,
                    "fabric_fit_verdict": verdict,
                    "fit_experience": emotional.get(verdict, emotional["aligned"]),
                    "siren": SIREN_SELL,
                    "patente": PATENTE,
                    "product_lane": PRODUCT_LANE,
                    "protocol": "zero_size",
                },
            )
            return

        if path in ("/api/v1/inventory/match",):
            from inventory_engine import inventory_match_payload

            try:
                data = body_json if isinstance(body_json, dict) else {}
                out = inventory_match_payload(data)
                _send_json(self, {"ok": True, **out, "siren": SIREN_SELL, "patente": PATENTE})
            except Exception:
                _send_json_error(self, 500, "Erreur moteur inventaire Divineo")
            return

        if path in ("/api/v1/mirror/snap",):
            from inventory_engine import inventory_match_payload

            sil = {
                "fabric_fit_verdict": str(body_json.get("fabric_fit_verdict", "") or ""),
                "fabric_sensation": str(body_json.get("fabric_sensation", "") or ""),
                "snap": True,
            }
            inv = inventory_match_payload(sil)
            response = _jules_payload()
            combo = (
                f"{response.get('jules_msg', '').strip()}\n\n"
                f"{inv.get('message', '').strip()}"
            ).strip()
            response["jules_msg"] = combo
            response["inventory_match"] = inv
            response["product_lane"] = PRODUCT_LANE
            response["anti_accumulation"] = True
            response["single_size_certitude"] = True
            response["quality_control_address"] = (
                "27 Rue de Argenteuil, 75001 Paris, France"
            )
            _slack_notify(
                "TryOnYou · Mirror SNAP + inventaire réel\n"
                f"{inv.get('garment_id', '')} · {PATENTE}"
            )
            maybe_log_ttc_unlock_event(self)
            _send_json(self, response)
            return

        if path in ("/api/v1/checkout/perfect-selection",):
            raw_sens = body_json.get("fabric_sensation")
            sensation = (
                str(raw_sens).strip()
                if raw_sens is not None
                else "ajustage parfait — protocole Zero-Size"
            )[:240]
            raw_flow = body_json.get("shopping_flow")
            flow = (
                str(raw_flow).strip() if raw_flow is not None else "non_stop_card"
            )[:64]
            meta = {
                "protocol": "zero_size",
                "checkout": True,
                "fabric_sensation": sensation,
                "shopping_flow": flow,
                "anti_accumulation": True,
                "single_size_certitude": True,
            }
            try:
                lead_id, ts = _insert_lead(
                    "selection",
                    "ofrenda_v10_checkout",
                    None,
                    meta,
                )
            except OSError:
                lead_id, ts = 0, datetime.now(timezone.utc).isoformat()

            shop_u, amz_u = _perfect_checkout_urls(lead_id, sensation)
            primary = str(
                os.environ.get("CHECKOUT_PRIMARY_CHANNEL", "shopify") or "shopify"
            ).lower()
            primary_url = amz_u if primary == "amazon" else shop_u
            if not primary_url:
                primary_url = shop_u or amz_u
            if not primary_url:
                primary_url = amz_u if primary == "shopify" else shop_u

            emotional_seal = (
                "Votre silhouette a trouvé son équilibre — une seule taille, "
                "celle du scan : acquisition Divineo, anti-accumulation (sans M/L/XL « au cas où »)."
            )
            if not (shop_u or amz_u):
                emotional_seal = (
                    "Parcours Divineo enregistré — configurez les ponts Shopify ou Amazon "
                    "dans Vercel pour ouvrir le paiement (SIREN scellé, Zero-Size intact)."
                )

            payload = {
                "ok": True,
                "lead_id": lead_id,
                "timestamp_iso": ts,
                "emotional_seal": emotional_seal,
                "checkout_shopify_url": shop_u or "",
                "checkout_amazon_url": amz_u or "",
                "checkout_primary_url": primary_url or "",
                "siren": SIREN_SELL,
                "patente": PATENTE,
                "product_lane": PRODUCT_LANE,
                "protocol": "zero_size",
                "shopping_flow": flow,
                "anti_accumulation": True,
                "single_size_certitude": True,
                "quality_control_address": "27 Rue de Argenteuil, 75001 Paris, France",
            }
            _slack_notify(
                f"TryOnYou · checkout Zero-Size · ANTI-ACCUMULATION · lead {lead_id} · "
                f"{PATENTE} · SIREN {SIREN_SELL}"
            )
            _make_forward_lead(payload)
            _send_json(self, payload)
            return

        response = _jules_payload()
        _slack_notify(
            "TryOnYou FIS · POST Jules\n"
            f"{response.get('protocolo', '')} · {response.get('patente', '')}"
        )
        _send_json(self, response)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        path_key = path.rstrip("/") or "/"

        if path_key in ("/api/health", "/api/v1/health"):
            if bunker_blackout_mode():
                _maybe_slack_sistema_suspendido()
            _send_json(
                self,
                {
                    "ok": True,
                    "service": "jules_omega",
                    "siren": SIREN_SELL,
                    "patente": PATENTE,
                    "product_lane": PRODUCT_LANE,
                    "protocol": "zero_size",
                    "bunker_blackout": bunker_blackout_mode(),
                },
            )
            return

        if path_key in ("/api/v1/inventory/status",):
            if _inventory_kill_paths_block("GET", path_key):
                _respond_inventory_locked(self, path_key, "GET")
                return
            from inventory_engine import inventory_status_payload

            maybe_log_ttc_unlock_event(self)
            _send_json(self, {"ok": True, **inventory_status_payload()})
            return

        static_file = _resolve_safe_static(path)
        if static_file is not None:
            ext = os.path.splitext(static_file)[1].lower()
            mime = _MIME.get(ext, "application/octet-stream")
            with open(static_file, "rb") as f:
                _send_binary(self, f.read(), mime)
            return

        if path_key in (
            "/mirror_sanctuary_v10.html",
            "/mirror_sanctuary_v10",
        ):
            sanctuary = _html_mirror_sanctuary()
            if sanctuary is not None:
                _send_binary(self, sanctuary, "text/html; charset=utf-8")
            return

        html_body = _html_index_body()
        if html_body is not None:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(html_body)))
            self.end_headers()
            self.wfile.write(html_body)
            return
        plain = (
            "TRYONYOU V10 Omega — búnker opérationnel. Build UI: npm run build → dist/"
        ).encode()
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(plain)))
        self.end_headers()
        self.wfile.write(plain)


def _cli_main() -> int:
    parser = argparse.ArgumentParser(
        description="TryOnYou API — acciones auxiliares desde terminal.",
    )
    parser.add_argument(
        "--action",
        default="",
        help="send_bpifrance_emergency: genera borradores Bpifrance en operacion_rescate/",
    )
    args = parser.parse_args()
    if not args.action:
        print(
            "Uso: python3 api/index.py --action send_bpifrance_emergency",
            file=sys.stderr,
        )
        return 2
    if args.action == "send_bpifrance_emergency":
        root = _project_root()
        if root not in sys.path:
            sys.path.insert(0, root)
        from solicitud_liquidez_bpifrance_v10 import main as bpifrance_main

        return bpifrance_main()
    print(f"Acción desconocida: {args.action!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli_main())

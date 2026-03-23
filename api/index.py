from http.server import BaseHTTPRequestHandler
import json
import os


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _stripe_links() -> tuple[str, str]:
    """Enlaces Payment Link (Vercel): define STRIPE_LINK_* o VITE_STRIPE_LINK_*."""
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


def _html_index_body() -> bytes | None:
    """Sirve index.html o plantilla V10; inyecta enlaces Stripe desde entorno."""
    root = _project_root()
    link_45, link_98 = _stripe_links()
    for rel in ("index.html", os.path.join("src", "templates", "mirror_v10_final.html")):
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


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        link_45, link_98 = _stripe_links()
        response = {
            "status": "DIVINEO_ACTIVE",
            "jules_msg": "Bonjour, c'est Jules. Recibido. El arquitecto Rubén E. está validando su precisión. Hablamos en un 'snap'.",
            "protocolo": "V10.4_Lafayette",
            "next_step": "A fuego!",
            "patente": "PCT/EP2025/067317",
            "stripe_link_sovereignty_4_5m_eur": link_45 if link_45 != "#" else "",
            "stripe_link_sovereignty_98k_eur": link_98 if link_98 != "#" else "",
        }
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        html_body = _html_index_body()
        if html_body is not None:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_body)
            return
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Búnker 75005 Operativo. tryonyou-app V10.4 Online.".encode())

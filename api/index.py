from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse


def _project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def _html_index_body() -> bytes | None:
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


def _serve_file(handler, rel_path: str, content_type: str, cache: str = "public, max-age=86400"):
    root = _project_root()
    filepath = os.path.normpath(os.path.join(root, rel_path))
    if not filepath.startswith(os.path.normpath(root + os.sep)):
        handler.send_response(403)
        handler.send_header("Content-Length", "0")
        handler.end_headers()
        return
    if not os.path.isfile(filepath):
        msg = f"{rel_path} not found".encode()
        handler.send_response(404)
        handler.send_header("Content-type", "text/plain; charset=utf-8")
        handler.send_header("Content-Length", str(len(msg)))
        handler.end_headers()
        handler.wfile.write(msg)
        return
    with open(filepath, "rb") as f:
        data = f.read()
    handler.send_response(200)
    handler.send_header("Content-type", content_type)
    handler.send_header("Cache-Control", cache)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Accept-Ranges", "bytes")
    handler.end_headers()
    handler.wfile.write(data)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
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
        body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        # Static assets
        if path == "/hero.mp4":
            _serve_file(self, "hero.mp4", "video/mp4", "public, max-age=604800")
            return
        if path == "/lafayette_collection.json":
            _serve_file(self, "src/data/lafayette_collection.json", "application/json; charset=utf-8", "public, max-age=3600")
            return
        if path == "/logo_pavo_real.png":
            _serve_file(self, "logo_pavo_real.png", "image/png")
            return

        # Main HTML
        html_body = _html_index_body()
        if html_body is not None:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_body)))
            self.end_headers()
            self.wfile.write(html_body)
            return

        plain = "Búnker 75005 Operativo. tryonyou-app V10.4 Online.".encode()
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(plain)))
        self.end_headers()
        self.wfile.write(plain)

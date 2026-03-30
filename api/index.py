from http.server import BaseHTTPRequestHandler
import argparse
import json
import os
import sys
from urllib.parse import urlparse

# Extensions servidas comme fichiers statiques (Vercel: sinon tout GET tombait sur index.html).
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
}


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


def _resolve_safe_static(path: str) -> str | None:
    """Chemin URL → fichier bajo la raíz del repo; None si no es estático seguro."""
    root = _project_root()
    root_prefix = os.path.normpath(root + os.sep)
    if path.startswith("/"):
        path = path[1:]
    if not path or path.endswith("/"):
        return None
    candidate = os.path.normpath(os.path.join(root, path))
    if not candidate.startswith(root_prefix):
        return None
    if not os.path.isfile(candidate):
        return None
    ext = os.path.splitext(candidate)[1].lower()
    if ext not in _STATIC_EXTS:
        return None
    rel = os.path.relpath(candidate, root)
    if rel.startswith("..") or os.path.isabs(rel):
        return None
    if rel == "index.html" or rel.startswith(".git" + os.sep) or rel.startswith("api" + os.sep):
        return None
    return candidate


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
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        link_45, link_98 = _stripe_links()
        response = {
            "status": "DIVINEO_ACTIVE",
            "jules_msg": "Bonjour, c'est Jules. Recibido. El arquitecto Rubén Espinar Rodríguez está validando su precisión. Hablamos en un 'snap'.",
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
        path_key = path.rstrip("/") or "/"

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


def _cli_main() -> int:
    """CLI local (no afecta el handler Vercel)."""
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

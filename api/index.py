from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "status": "DIVINEO_ACTIVE",
            "jules_msg": "Bonjour, c'est Jules. Recibido. El arquitecto Rubén E. está validando su precisión. Hablamos en un 'snap'.",
            "protocolo": "V10.4_Lafayette",
            "next_step": "A fuego!"
        }
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Búnker 75005 Operativo. tryonyou-app V10.4 Online.".encode())

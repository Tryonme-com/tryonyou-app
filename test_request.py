import asyncio
import time
import httpx
import hmac
import hashlib
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class MockWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass

def run_mock_server():
    server = HTTPServer(('localhost', 8001), MockWebhookHandler)
    server.serve_forever()

SLACK_SIGNING_SECRET = "test_secret"

def generate_slack_signature(secret, timestamp, body):
    sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    signature = "v0=" + hmac.new(
        secret.encode("utf-8"),
        sig_basestring,
        hashlib.sha256,
    ).hexdigest()
    return signature

async def main():
    webhook_thread = threading.Thread(target=run_mock_server, daemon=True)
    webhook_thread.start()

    timestamp = str(int(time.time()))
    payload = {
        "actions": [{"value": f"ref_0", "action_id": "approve"}],
        "user": {"name": f"user_0"},
        "response_url": "http://localhost:8001/webhook"
    }
    body = f"payload={json.dumps(payload)}"
    signature = generate_slack_signature(SLACK_SIGNING_SECRET, timestamp, body)

    headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": signature,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    env = os.environ.copy()
    env["SLACK_SIGNING_SECRET"] = SLACK_SIGNING_SECRET
    env["SLACK_WEBHOOK_URL"] = "http://localhost:8001/webhook"
    env["AUDIT_DB_PATH"] = "benchmark.db"

    server_process = subprocess.Popen(
        ["uvicorn", "main_engine:app", "--port", "8000"],
        env=env
        #stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL
    )

    time.sleep(2)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/api/slack/interact", content=body, headers=headers)
            print(response.status_code, response.text)
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    asyncio.run(main())

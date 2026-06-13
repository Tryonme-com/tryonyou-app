import asyncio
import time
import httpx
import hmac
import hashlib
import json
import subprocess
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3

SLACK_SIGNING_SECRET = "test_secret"
PORT = 8000
WEBHOOK_PORT = 8001
WEBHOOK_URL = f"http://localhost:{WEBHOOK_PORT}/webhook"

class MockWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass # Suppress logs

def run_mock_server():
    server = HTTPServer(('localhost', WEBHOOK_PORT), MockWebhookHandler)
    server.serve_forever()

def generate_slack_signature(secret, timestamp, body):
    sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    signature = "v0=" + hmac.new(
        secret.encode("utf-8"),
        sig_basestring,
        hashlib.sha256,
    ).hexdigest()
    return signature

async def send_request(client, i):
    timestamp = str(int(time.time()))
    payload = {
        "actions": [{"value": f"ref_{i}", "action_id": "approve"}],
        "user": {"name": f"user_{i}"},
        "response_url": WEBHOOK_URL
    }

    body = f"payload={json.dumps(payload)}"
    signature = generate_slack_signature(SLACK_SIGNING_SECRET, timestamp, body)

    headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": signature,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    start_time = time.time()
    response = await client.post(f"http://localhost:{PORT}/api/slack/interact", content=body, headers=headers)
    end_time = time.time()

    return response.status_code, end_time - start_time

async def run_benchmark(num_requests):
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=num_requests)) as client:
        tasks = [send_request(client, i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Start mock webhook server
    webhook_thread = threading.Thread(target=run_mock_server, daemon=True)
    webhook_thread.start()

    # Start uvicorn server
    env = os.environ.copy()
    env["SLACK_SIGNING_SECRET"] = SLACK_SIGNING_SECRET
    env["SLACK_WEBHOOK_URL"] = WEBHOOK_URL
    env["AUDIT_DB_PATH"] = "benchmark.db"

    if os.path.exists("benchmark.db"):
        os.remove("benchmark.db")

    server_process = subprocess.Popen(
        ["uvicorn", "main_engine:app", "--port", str(PORT)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        time.sleep(2)
        asyncio.run(run_benchmark(50))
    finally:
        server_process.terminate()
        server_process.wait()

    with sqlite3.connect("benchmark.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM refs")
        print("Final Row count:", cursor.fetchone()[0])

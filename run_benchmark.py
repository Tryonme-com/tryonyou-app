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

SLACK_SIGNING_SECRET = "test_secret"
PORT = 8000
WEBHOOK_PORT = 8001
WEBHOOK_URL = f"http://localhost:{WEBHOOK_PORT}/webhook"
CONCURRENT_REQUESTS = 200

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

async def run_benchmark():
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=CONCURRENT_REQUESTS)) as client:
        start_time = time.time()
        tasks = [send_request(client, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        successes = sum(1 for status, _ in results if status == 200)
        total_time = end_time - start_time
        latencies = [latency for _, latency in results]

        print(f"Benchmark Results:")
        print(f"Total requests: {CONCURRENT_REQUESTS}")
        print(f"Successful requests: {successes}")
        print(f"Total time: {total_time:.4f} seconds")
        print(f"Throughput: {CONCURRENT_REQUESTS / total_time:.2f} req/s")
        print(f"Avg latency: {sum(latencies) / len(latencies):.4f} seconds")
        print(f"Max latency: {max(latencies):.4f} seconds")

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
        # Wait for server to start
        time.sleep(2)
        asyncio.run(run_benchmark())
    finally:
        server_process.terminate()
        server_process.wait()

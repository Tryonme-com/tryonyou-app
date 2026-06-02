"""Fetch and pretty-print Vercel function runtime logs for the last invocations."""
import json
import os
import sys
import urllib.request
import urllib.parse

VERCEL_TOKEN = os.environ.get("VERCEL_TOKEN")
VERCEL_PROJECT_ID = os.environ.get("VERCEL_PROJECT_ID")
VERCEL_ORG_ID = os.environ.get("VERCEL_ORG_ID")
VERCEL_DEPLOYMENT_ID = os.environ.get("VERCEL_DEPLOYMENT_ID")


def _required_env(name, value):
    result = (value or "").strip()
    if not result:
        sys.exit(f"Error: {name} environment variable is required.")
    return result


TOKEN = _required_env("VERCEL_TOKEN", VERCEL_TOKEN)
TEAM = _required_env("VERCEL_ORG_ID", VERCEL_ORG_ID)
PROJECT = _required_env("VERCEL_PROJECT_ID", VERCEL_PROJECT_ID)
DEPLOYMENT = sys.argv[1] if len(sys.argv) > 1 else (VERCEL_DEPLOYMENT_ID or "").strip()
if not DEPLOYMENT:
    sys.exit("Error: provide the deployment id as the first CLI argument or VERCEL_DEPLOYMENT_ID.")


def call(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


# Try the v1/projects logs endpoint
endpoints = [
    f"https://api.vercel.com/v3/deployments/{DEPLOYMENT}/events?teamId={TEAM}&direction=backward&limit=200&types=stdout,stderr,deployment-state,fatal,error",
    f"https://api.vercel.com/v2/deployments/{DEPLOYMENT}/events?teamId={TEAM}&direction=backward&limit=200&follow=0",
]
for url in endpoints:
    print(f"--- {url}")
    try:
        d = call(url)
        events = d if isinstance(d, list) else d.get("events", [])
        print(f"  events: {len(events)}")
        for e in events[:80]:
            t = e.get("type")
            text = (e.get("payload") or {}).get("text") or e.get("text") or ""
            if isinstance(text, dict):
                text = json.dumps(text)
            print(f"  [{t}] {text[:300]}")
    except Exception as ex:
        print(f"  ERROR {ex}")

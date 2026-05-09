"""Fetch and pretty-print Vercel function runtime logs for the last invocations."""
import json
import os
import sys
import urllib.request
import urllib.parse

TOKEN = os.environ.get("VERCEL_TOKEN", "VERCEL_TOKEN_REDACTED")
TEAM = "team_SDhj8kxLVE7oJ3S5KPbwG9uC"
PROJECT = "prj_vDPvZ4U1MD4t3CmKxfusBB7md2Fh"
DEPLOYMENT = sys.argv[1] if len(sys.argv) > 1 else "dpl_6afqyDxd6vgiCT4k4geG5SFDjvQg"


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

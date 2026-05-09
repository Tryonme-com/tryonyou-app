"""
Direct Vercel deployment for TRYONYOU — uploads files via the v2/files API,
then creates a v13/deployments record targeted at production. No GitHub push.

Env / constants:
  - VERCEL_TOKEN   : auth token (Bearer)
  - VERCEL_TEAM_ID : team_SDhj8kxLVE7oJ3S5KPbwG9uC
  - VERCEL_PROJECT : prj_vDPvZ4U1MD4t3CmKxfusBB7md2Fh (id) / tryonyou-app (name)

Bundles:
  - dist/public/**         → site static  (deployed as `*` files, root)
  - api/index.py           → serverless function
  - api/requirements.txt   → python deps
  - vercel.json            → routing + functions config
  - package.json (minimal) → ensures Vercel recognizes outputDirectory
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib import request as urlrequest
from urllib import error as urlerror

ROOT = Path(__file__).resolve().parent.parent
TEAM_ID = "team_SDhj8kxLVE7oJ3S5KPbwG9uC"
PROJECT_ID = "prj_vDPvZ4U1MD4t3CmKxfusBB7md2Fh"
PROJECT_NAME = "tryonyou-app"
TOKEN = os.environ.get("VERCEL_TOKEN") or sys.argv[1] if len(sys.argv) > 1 else os.environ.get("VERCEL_TOKEN", "")

if not TOKEN:
    print("ERROR: pass token as $VERCEL_TOKEN or first CLI arg")
    sys.exit(2)

API = "https://api.vercel.com"
HEADERS_BASE = {"Authorization": f"Bearer {TOKEN}"}


def _http(method: str, url: str, *, headers: dict | None = None,
          data: bytes | None = None, json_body: Any = None,
          timeout: int = 60) -> tuple[int, dict | bytes]:
    h = dict(HEADERS_BASE)
    if headers:
        h.update(headers)
    body = data
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    req = urlrequest.Request(url, data=body, headers=h, method=method)
    try:
        with urlrequest.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if "application/json" in ct:
                return resp.status, json.loads(raw.decode("utf-8") or "{}")
            return resp.status, raw
    except urlerror.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return e.code, raw


def collect_files() -> list[tuple[str, Path]]:
    """Return [(deploy_path, local_path)] pairs for the deployment."""
    pairs: list[tuple[str, Path]] = []

    static_root = ROOT / "dist" / "public"
    if not static_root.exists():
        raise SystemExit(f"missing build output: {static_root}")
    for p in sorted(static_root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(static_root).as_posix()
            pairs.append((rel, p))

    api_dir = ROOT / "api"
    for name in ("index.py", "requirements.txt"):
        f = api_dir / name
        if f.exists():
            pairs.append((f"api/{name}", f))

    # Use the production-targeted vercel.json (no build/install commands)
    prod_cfg = ROOT / "scripts" / "prod_vercel.json"
    if prod_cfg.exists():
        pairs.append(("vercel.json", prod_cfg))
    else:
        f = ROOT / "vercel.json"
        if f.exists():
            pairs.append(("vercel.json", f))

    # Minimal package.json so Vercel does not run install / detect framework
    pkg = {
        "name": PROJECT_NAME,
        "version": "1.0.0",
        "private": True,
    }
    pkg_bytes = json.dumps(pkg, indent=2).encode("utf-8")
    tmp_pkg = ROOT / "dist" / "_pkg_for_vercel.json"
    tmp_pkg.write_bytes(pkg_bytes)
    pairs.append(("package.json", tmp_pkg))

    return pairs


def upload_one(deploy_path: str, local: Path) -> dict:
    data = local.read_bytes()
    sha1 = hashlib.sha1(data).hexdigest()
    size = len(data)

    url = f"{API}/v2/files?teamId={TEAM_ID}"
    headers = {
        "Content-Type": "application/octet-stream",
        "x-vercel-digest": sha1,
        "x-vercel-size": str(size),
    }
    status, resp = _http("POST", url, headers=headers, data=data, timeout=180)
    if status not in (200, 201):
        raise SystemExit(f"upload failed {deploy_path}: {status} {resp}")
    return {"file": deploy_path, "sha": sha1, "size": size}


def create_deployment(file_records: list[dict]) -> dict:
    files_payload = [
        {"file": fr["file"], "sha": fr["sha"], "size": fr["size"]}
        for fr in file_records
    ]
    body = {
        "name": PROJECT_NAME,
        "project": PROJECT_ID,
        "target": "production",
        "files": files_payload,
        "projectSettings": {
            "framework": None,
            "buildCommand": "",
            "installCommand": "",
            "outputDirectory": ".",
            "devCommand": "",
            "rootDirectory": None,
            "nodeVersion": "20.x",
        },
    }
    url = f"{API}/v13/deployments?teamId={TEAM_ID}&forceNew=1&skipAutoDetectionConfirmation=1"
    status, resp = _http("POST", url, json_body=body, timeout=180)
    if status not in (200, 201, 202):
        raise SystemExit(f"deployment creation failed: {status} {resp}")
    return resp  # type: ignore[return-value]


def wait_deployment(dep_id: str, timeout_s: int = 300) -> dict:
    url = f"{API}/v13/deployments/{dep_id}?teamId={TEAM_ID}"
    deadline = time.time() + timeout_s
    last: dict = {}
    while time.time() < deadline:
        status, resp = _http("GET", url, timeout=30)
        if isinstance(resp, dict):
            last = resp
            state = resp.get("readyState") or resp.get("status") or "?"
            print(f"  state: {state}")
            if state in ("READY", "ERROR", "CANCELED"):
                return resp
        time.sleep(5)
    return last


def main() -> None:
    print(f"[deploy] root: {ROOT}")
    pairs = collect_files()
    total_size = sum(p.stat().st_size for _, p in pairs)
    print(f"[deploy] files: {len(pairs)}  total: {total_size/1024:.1f} KB")
    for dp, lp in pairs:
        print(f"   • {dp:<55s} {lp.stat().st_size:>8d} B")

    print("[deploy] uploading…")
    records: list[dict] = []
    for i, (dp, lp) in enumerate(pairs, 1):
        rec = upload_one(dp, lp)
        records.append(rec)
        print(f"   [{i:>2}/{len(pairs)}] {dp}  sha={rec['sha'][:10]}…  {rec['size']} B")

    print("[deploy] creating deployment record…")
    dep = create_deployment(records)
    dep_id = dep.get("id") or dep.get("uid")
    url = dep.get("url") or dep.get("alias") or "(no url)"
    print(f"[deploy] id={dep_id}  url={url}")

    print("[deploy] waiting for READY…")
    final = wait_deployment(dep_id) if dep_id else dep
    state = final.get("readyState") or final.get("status")
    print(f"[deploy] final state: {state}")
    if state == "READY":
        print(f"[deploy] OK → https://{final.get('url') or url}")
    else:
        print("[deploy] non-ready final payload (truncated):")
        print(json.dumps(final, indent=2)[:2000])


if __name__ == "__main__":
    main()

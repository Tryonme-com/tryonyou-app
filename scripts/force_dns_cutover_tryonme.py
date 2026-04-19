"""
Forzar cutover DNS de TryOnMe hacia Vercel (76.76.21.21).

Soporta Cloudflare con:
  - Token: CLOUDFLARE_API_TOKEN o CF_API_TOKEN
  - o Email/Key: CLOUDFLARE_EMAIL + CLOUDFLARE_API_KEY

Zonas:
  - CLOUDFLARE_ZONE_ID_TRYONME_APP (recomendado)
  - CLOUDFLARE_ZONE_ID_TRYONME_COM (recomendado)
  - fallback: CLOUDFLARE_ZONE_ID / CF_ZONE_ID

Uso:
  python3 scripts/force_dns_cutover_tryonme.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

TARGET_IP = "76.76.21.21"


@dataclass(frozen=True)
class DnsTarget:
    zone_env: str
    zone_fallback_allowed: bool
    fqdn: str
    proxied: bool = False


TARGETS: tuple[DnsTarget, ...] = (
    DnsTarget("CLOUDFLARE_ZONE_ID_TRYONME_APP", True, "tryonme.app"),
    DnsTarget("CLOUDFLARE_ZONE_ID_TRYONME_COM", True, "tryonme.com"),
    DnsTarget("CLOUDFLARE_ZONE_ID_TRYONME_COM", True, "www.tryonme.com"),
)


def _auth_headers() -> dict[str, str]:
    token = (
        os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
        or os.getenv("CF_API_TOKEN", "").strip()
    )
    if token:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    email = os.getenv("CLOUDFLARE_EMAIL", "").strip()
    api_key = os.getenv("CLOUDFLARE_API_KEY", "").strip()
    if email and api_key:
        return {
            "X-Auth-Email": email,
            "X-Auth-Key": api_key,
            "Content-Type": "application/json",
        }
    return {}


def _zone_id(target: DnsTarget) -> str:
    direct = os.getenv(target.zone_env, "").strip()
    if direct:
        return direct
    if target.zone_fallback_allowed:
        return (
            os.getenv("CLOUDFLARE_ZONE_ID", "").strip()
            or os.getenv("CF_ZONE_ID", "").strip()
        )
    return ""


def _request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: dict | None = None,
) -> dict:
    body = None
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    req = urllib.request.Request(url, method=method, headers=headers, data=body)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8"))


def _get_record(zone_id: str, fqdn: str, headers: dict[str, str]) -> dict | None:
    query = urllib.parse.urlencode({"type": "A", "name": fqdn, "per_page": 1})
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?{query}"
    data = _request_json("GET", url, headers)
    if not data.get("success"):
        raise RuntimeError(f"Cloudflare query failed for {fqdn}: {data.get('errors')}")
    result = data.get("result") or []
    return result[0] if result else None


def _upsert_a_record(zone_id: str, fqdn: str, proxied: bool, headers: dict[str, str]) -> None:
    existing = _get_record(zone_id, fqdn, headers)
    payload = {
        "type": "A",
        "name": fqdn,
        "content": TARGET_IP,
        "ttl": 60,
        "proxied": proxied,
    }
    if existing:
        record_id = str(existing.get("id", "")).strip()
        if not record_id:
            raise RuntimeError(f"Record ID missing for {fqdn}.")
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
        data = _request_json("PUT", url, headers, payload)
        if not data.get("success"):
            raise RuntimeError(f"Cloudflare update failed for {fqdn}: {data.get('errors')}")
        print(f"✓ Actualizado A {fqdn} -> {TARGET_IP}")
        return

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    data = _request_json("POST", url, headers, payload)
    if not data.get("success"):
        raise RuntimeError(f"Cloudflare create failed for {fqdn}: {data.get('errors')}")
    print(f"✓ Creado A {fqdn} -> {TARGET_IP}")


def main() -> int:
    print("--- [FORCE DNS CUTOVER TRYONME] ---")
    headers = _auth_headers()
    if not headers:
        print(
            "❌ Faltan credenciales Cloudflare (CLOUDFLARE_API_TOKEN/CF_API_TOKEN "
            "o CLOUDFLARE_EMAIL+CLOUDFLARE_API_KEY)."
        )
        return 2

    failures: list[str] = []
    for target in TARGETS:
        zone_id = _zone_id(target)
        if not zone_id:
            failures.append(f"{target.fqdn}: zona no configurada en entorno.")
            continue
        try:
            _upsert_a_record(zone_id, target.fqdn, target.proxied, headers)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", errors="replace")[:500]
            failures.append(f"{target.fqdn}: HTTP {e.code} {msg}")
        except Exception as e:  # noqa: BLE001
            failures.append(f"{target.fqdn}: {e}")

    if failures:
        print("⚠️  Cutover incompleto:")
        for f in failures:
            print(f" - {f}")
        return 1

    print("✅ Cutover DNS aplicado para primer chasquido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

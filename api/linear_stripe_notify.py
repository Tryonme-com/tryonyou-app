"""
Incidencias opcionales en Linear ante fallos Stripe (checkout, retrieve, etc.).

Requiere en entorno (nunca en git):
  LINEAR_API_KEY   — token de la API Linear (prefijo lin_api_…)
  LINEAR_TEAM_ID   — UUID del equipo (Settings → Teams en Linear)

No uses claves de Firebase/Google (p. ej. AIzaSy…) como LINEAR_API_KEY: no son compatibles.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_LINEAR_GQL = "https://api.linear.app/graphql"
_ISSUE_MUTATION = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { id identifier }
  }
}
"""


def notify_stripe_failure_optional(
    context: str,
    message: str,
    *,
    price_id: str | None = None,
    product_id: str | None = None,
) -> None:
    key = (os.getenv("LINEAR_API_KEY") or "").strip()
    team = (os.getenv("LINEAR_TEAM_ID") or "").strip()
    if not key or not team:
        return
    if not key.startswith("lin_api_"):
        logger.warning("linear_notify_skipped: LINEAR_API_KEY debe ser lin_api_… (no Firebase/Google)")
        return
    desc = f"{message}\n\ncontext={context}"
    if price_id:
        desc += f"\nprice_id={price_id}"
    if product_id:
        desc += f"\nproduct_id={product_id}"
    desc += "\n\nPatente PCT/EP2025/067317 — Stripe cuenta Paris (FR)."

    payload = {
        "query": _ISSUE_MUTATION.strip(),
        "variables": {
            "input": {
                "teamId": team,
                "title": f"[Stripe] {context}",
                "description": desc[:25000],
            }
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        _LINEAR_GQL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
        errs = body.get("errors")
        if errs:
            logger.warning("linear_issue_create_graphql_errors: %s", errs)
    except urllib.error.HTTPError as e:
        logger.warning("linear_issue_create_http_%s", e.code)
    except Exception as e:
        logger.warning("linear_issue_create_failed: %s", e)

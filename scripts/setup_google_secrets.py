"""
setup_google_secrets.py — upload all TRYONYOU secrets to Google Secret Manager.

Usage:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json
  export GCP_PROJECT_ID=my-gcp-project
  python scripts/setup_google_secrets.py [--env-file .env.local]

The script reads environment variables (from the shell or an optional .env file)
and creates or updates each secret version in Secret Manager.

Requires:
  pip install google-cloud-secret-manager
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# All secrets that must exist in Google Secret Manager for Cloud Run.
SECRETS: list[str] = [
    # ── API / Backend ──────────────────────────────────────────────────────
    "STRIPE_ENDPOINT_SECRET",
    "JULES_CRON_TOKEN",
    "GMAIL_REFRESH_TOKEN",
    "GMAIL_CLIENT_ID",
    "GMAIL_CLIENT_SECRET",
    "GEMINI_API_KEY",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "SPREADSHEET_ID",
    "PENNYLANE_API_KEY",
    "PAU_TTS_ENDPOINT",
    "PAU_TTS_FALLBACK_AUDIO_URL",
    # ── Server (Node) ──────────────────────────────────────────────────────
    "LINEAR_API_TOKEN",
    "GOOGLE_SHEETS_ID",
    "GOOGLE_SHEETS_ACCESS_TOKEN",
    # ── Scripts ────────────────────────────────────────────────────────────
    "VERCEL_TOKEN",
    "LINEAR_API_KEY",
    "LINEAR_PROJECT_ID",
    "LINEAR_TEAM_ID",
]

# Variables passed as plain env-vars to Cloud Run (no Secret Manager needed).
ENV_VARS: list[str] = [
    "LAFAYETTE_VERIFY_BASE_URL",
    "JULES_MAIL_MAX_RESULTS",
    "MAX_ENVIOS_DIARIOS",
    "GOOGLE_SHEETS_RANGE",
    "LINEAR_PAGE_SIZE",
    "LINEAR_MAX_PAGES",
    "LINEAR_SYNC_CRON_MS",
    # Frontend (Vite) — also set as GitHub Actions variables (vars.*):
    "VITE_OAUTH_PORTAL_URL",
    "VITE_APP_ID",
    "VITE_FRONTEND_FORGE_API_KEY",
    "VITE_FRONTEND_FORGE_API_URL",
    "VITE_ANALYTICS_ENDPOINT",
    "VITE_ANALYTICS_WEBSITE_ID",
]


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (avoids hard dependency on python-dotenv)."""
    if not path.exists():
        return
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _log_key(label: str, name: str) -> None:
    """Print only the key name, never a secret value."""
    print(f"  [{label:8}]  {name}")  # lgtm[py/clear-text-logging-sensitive-data]


def _upsert_secret(client, project: str, name: str, payload: bytes) -> None:
    from google.api_core.exceptions import NotFound, AlreadyExists

    parent = f"projects/{project}"
    secret_path = f"{parent}/secrets/{name}"

    # Create secret resource if it does not exist yet.
    created = False
    try:
        client.get_secret(name=secret_path)
    except NotFound:
        try:
            client.create_secret(
                parent=parent,
                secret_id=name,
                secret={"replication": {"automatic": {}}},
            )
            created = True
        except AlreadyExists:
            pass

    # Add a new version with the current value.
    client.add_secret_version(parent=secret_path, payload={"data": payload})
    verb = "created" if created else "updated"
    # Log only the key name, never the secret value.
    _log_key(verb, name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync secrets to Google Secret Manager")
    parser.add_argument("--env-file", default=".env.local", help="Optional .env file to load")
    parser.add_argument("--dry-run", action="store_true", help="Print key names without uploading")
    args = parser.parse_args()

    # Load optional .env file.
    _load_dotenv(Path(args.env_file))

    project = os.environ.get("GCP_PROJECT_ID", "").strip()
    if not project:
        print("ERROR: set GCP_PROJECT_ID before running this script.", file=sys.stderr)
        sys.exit(1)

    # Build presence map using only boolean flags — never pass values to logging.
    present: set[str] = {s for s in SECRETS if os.environ.get(s, "").strip()}
    missing: list[str] = [s for s in SECRETS if s not in present]

    if missing:
        print("WARNING: the following secrets have no value and will be skipped:")
        for m in missing:
            _log_key("missing", m)

    if args.dry_run:
        print("\n[dry-run] Secrets that WOULD be uploaded:")
        for s in SECRETS:
            _log_key("set" if s in present else "skipped", s)
        print("\n[dry-run] Plain env-vars (not uploaded to Secret Manager):")
        for v in ENV_VARS:
            status = "set" if os.environ.get(v, "").strip() else "not set"
            _log_key(status, v)
        return

    try:
        from google.cloud import secretmanager
    except ImportError:
        print(
            "ERROR: google-cloud-secret-manager is not installed.\n"
            "Run: pip install google-cloud-secret-manager",
            file=sys.stderr,
        )
        sys.exit(1)

    client = secretmanager.SecretManagerServiceClient()

    print(f"\nUploading secrets to project '{project}'...\n")
    for name in SECRETS:
        if name not in present:
            _log_key("skipped", name)
            continue
        # Encode value to bytes here so the raw string never touches a log call.
        raw = os.environ[name].strip().encode("utf-8")
        _upsert_secret(client, project, name, raw)

    print("\nDone. Plain env-vars to configure in Cloud Run or GitHub Actions vars:")
    for v in ENV_VARS:
        status = "set" if os.environ.get(v, "").strip() else "not set"
        _log_key(status, v)


if __name__ == "__main__":
    main()

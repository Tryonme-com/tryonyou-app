"""
setup_google_secrets.py — carga todos los secretos de TRYONYOU en
Google Secret Manager.

Uso:
  export GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/sa-key.json
  export GCP_PROJECT_ID=mi-proyecto-gcp
  python scripts/setup_google_secrets.py [--env-file .env.local]

El script lee las variables de entorno (de la shell o de un archivo .env
opcional) y crea o actualiza cada secreto en Secret Manager.

Requiere:
  pip install google-cloud-secret-manager python-dotenv
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


def _upsert_secret(client, project: str, name: str, value: str) -> None:
    from google.api_core.exceptions import NotFound, AlreadyExists

    parent = f"projects/{project}"
    secret_path = f"{parent}/secrets/{name}"

    # Create secret resource if it does not exist yet.
    try:
        client.get_secret(name=secret_path)
    except NotFound:
        try:
            client.create_secret(
                parent=parent,
                secret_id=name,
                secret={"replication": {"automatic": {}}},
            )
            print(f"  [created]  {name}")
        except AlreadyExists:
            pass

    # Add a new version with the current value.
    client.add_secret_version(
        parent=secret_path,
        payload={"data": value.encode("utf-8")},
    )
    print(f"  [updated]  {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync secrets to Google Secret Manager")
    parser.add_argument("--env-file", default=".env.local", help="Optional .env file to load")
    parser.add_argument("--dry-run", action="store_true", help="Print values without uploading")
    args = parser.parse_args()

    # Load optional .env file.
    _load_dotenv(Path(args.env_file))

    project = os.environ.get("GCP_PROJECT_ID", "").strip()
    if not project:
        print("ERROR: set GCP_PROJECT_ID before running this script.", file=sys.stderr)
        sys.exit(1)

    missing = [s for s in SECRETS if not os.environ.get(s, "").strip()]
    if missing:
        print("WARNING: the following secrets have no value and will be skipped:")
        for m in missing:
            print(f"  - {m}")

    if args.dry_run:
        print("\n[dry-run] Secrets that WOULD be uploaded:")
        for s in SECRETS:
            val = os.environ.get(s, "")
            status = "<set>" if val else "<empty — skipped>"
            print(f"  {s}: {status}")
        print("\n[dry-run] Plain env-vars (not uploaded to Secret Manager):")
        for v in ENV_VARS:
            print(f"  {v} = {os.environ.get(v, '<not set>')}")
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
        value = os.environ.get(name, "").strip()
        if not value:
            print(f"  [skipped]  {name}  (empty)")
            continue
        _upsert_secret(client, project, name, value)

    print("\nDone. Plain env-vars to configure in Cloud Run or GitHub Actions vars:")
    for v in ENV_VARS:
        print(f"  {v} = {os.environ.get(v, '<not set>')}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Audit secrets/variables injection in GitHub Actions workflows.

Usage:
    python scripts/audit_injection.py --dry-run
    python scripts/audit_injection.py --workflow .github/workflows/deploy.yml
"""

import argparse
import re
import sys
from pathlib import Path

# ── Expected configuration ─────────────────────────────────────────────────
REQUIRED_SECRETS = {
    "GITHUB_TOKEN": "Auto-provisioned by GitHub Actions — no manual configuration needed",
    "GCP_SA_KEY": "Service Account JSON key for GCP authentication (base64 or raw JSON)",
    "FIREBASE_SERVICE_ACCOUNT": "Firebase service account JSON for Hosting deploys",
    "STRIPE_ENDPOINT_SECRET": "Stripe webhook signing secret",
    "GEMINI_API_KEY": "Google Gemini API key",
    "GMAIL_CLIENT_ID": "Gmail OAuth2 client ID",
    "GMAIL_CLIENT_SECRET": "Gmail OAuth2 client secret",
    "GMAIL_REFRESH_TOKEN": "Gmail OAuth2 refresh token",
    "GOOGLE_SERVICE_ACCOUNT_JSON": "Google service account JSON (Sheets / Drive)",
    "JULES_CRON_TOKEN": "Authentication token for cron endpoints",
    "PENNYLANE_API_KEY": "Pennylane accounting API key",
    "SPREADSHEET_ID": "Google Sheets spreadsheet ID",
    "PAU_TTS_ENDPOINT": "TTS service endpoint URL",
    "PAU_TTS_FALLBACK_AUDIO_URL": "Fallback audio URL for TTS",
    "LAFAYETTE_VERIFY_BASE_URL": "Lafayette verification base URL",
    "MAX_ENVIOS_DIARIOS": "Maximum daily sends cap",
    "VITE_OAUTH_PORTAL_URL": "OAuth portal URL injected at build time",
    "VITE_APP_ID": "App ID injected at build time",
    "VITE_FRONTEND_FORGE_API_KEY": "Forge API key injected at build time",
    "VITE_FRONTEND_FORGE_API_URL": "Forge API URL injected at build time",
    "VITE_ANALYTICS_ENDPOINT": "Analytics endpoint injected at build time",
    "VITE_ANALYTICS_WEBSITE_ID": "Analytics website ID injected at build time",
}

REQUIRED_VARS = {
    "GCP_PROJECT_ID": "GCP project ID — add via Settings → Secrets and variables → Variables",
}

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _parse_workflow(path: Path) -> tuple[set[str], set[str]]:
    """Return (secrets_found, vars_found) referenced in the workflow file."""
    text = path.read_text()
    secrets = set(re.findall(r"\$\{\{\s*secrets\.(\w+)\s*\}\}", text))
    vars_ = set(re.findall(r"\$\{\{\s*vars\.(\w+)\s*\}\}", text))
    return secrets, vars_


def _check(label: str, found: set[str], expected: dict[str, str], dry_run: bool) -> list[str]:
    issues: list[str] = []
    all_keys = sorted(expected.keys() | found)

    for key in all_keys:
        in_workflow = key in found
        documented = key in expected

        suffix = " (dry-run)" if dry_run else ""
        if in_workflow and documented:
            desc = expected[key]
            print(f"  {GREEN}✔{suffix}{RESET}  {BOLD}{key}{RESET}  —  {desc}")
        elif in_workflow and not documented:
            print(f"  {YELLOW}?{suffix}{RESET}  {BOLD}{key}{RESET}  —  referenced in workflow but undocumented")
        elif documented and not in_workflow:
            issues.append(key)
            print(f"  {RED}✘{suffix}{RESET}  {BOLD}{key}{RESET}  —  {expected[key]}")

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit GitHub Actions secrets/variables injection.")
    parser.add_argument(
        "--workflow",
        default=".github/workflows/deploy.yml",
        help="Path to the workflow YAML file (default: .github/workflows/deploy.yml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be checked without making any changes",
    )
    args = parser.parse_args()

    workflow_path = Path(args.workflow)
    if not workflow_path.exists():
        print(f"{RED}Error:{RESET} workflow file not found: {workflow_path}", file=sys.stderr)
        sys.exit(1)

    mode = " [DRY-RUN]" if args.dry_run else ""
    print(f"\n{BOLD}═══ Injection audit{mode}: {workflow_path} ═══{RESET}\n")

    secrets_found, vars_found = _parse_workflow(workflow_path)

    print(f"{BOLD}── Secrets (Settings → Secrets and variables → Actions → Secrets) ──{RESET}")
    secret_issues = _check("secrets", secrets_found, REQUIRED_SECRETS, args.dry_run)

    print(f"\n{BOLD}── Variables (Settings → Secrets and variables → Actions → Variables) ──{RESET}")
    var_issues = _check("vars", vars_found, REQUIRED_VARS, args.dry_run)

    print()
    if secret_issues or var_issues:
        print(f"{RED}{BOLD}✘ Missing configuration:{RESET}")
        for k in secret_issues:
            print(f"   • Secret  : {k}")
        for k in var_issues:
            print(f"   • Variable: {k}")
        print()
        print("Configure them at:")
        print("  https://github.com/Tryonme-com/tryonyou-app/settings/secrets/actions")
        if args.dry_run:
            print(f"\n{YELLOW}(dry-run — no changes made){RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}{BOLD}✔ All required secrets and variables are accounted for.{RESET}")
        if args.dry_run:
            print(f"{YELLOW}(dry-run — no changes made){RESET}")


if __name__ == "__main__":
    main()

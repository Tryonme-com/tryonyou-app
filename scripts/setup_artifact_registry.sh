#!/usr/bin/env bash
# Provision the Artifact Registry repository used by the Cloud Run deploy pipeline.
#
# Prerequisites:
#   gcloud CLI installed and authenticated with an account that has
#   the "Artifact Registry Administrator" role on the target project.
#
# Usage:
#   export GCP_PROJECT_ID=your-project-id
#   bash scripts/setup_artifact_registry.sh
#   bash scripts/setup_artifact_registry.sh --dry-run

set -euo pipefail

REPO_NAME="tryonyou"
REGION="europe-west1"
FORMAT="docker"
DESCRIPTION="Docker images for tryonyou Cloud Run services"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
  echo "❌  GCP_PROJECT_ID is not set."
  echo "    Export it first:  export GCP_PROJECT_ID=your-project-id"
  exit 1
fi

echo ""
echo "═══ Artifact Registry setup ═══"
echo "  Project : ${GCP_PROJECT_ID}"
echo "  Region  : ${REGION}"
echo "  Repo    : ${REPO_NAME}"
echo "  Format  : ${FORMAT}"
echo ""

if $DRY_RUN; then
  echo "🔍  [dry-run] Would run:"
  echo "    gcloud artifacts repositories create ${REPO_NAME} \\"
  echo "      --repository-format=${FORMAT} \\"
  echo "      --location=${REGION} \\"
  echo "      --description=\"${DESCRIPTION}\" \\"
  echo "      --project=${GCP_PROJECT_ID}"
  echo ""
  echo "    gcloud artifacts repositories describe ${REPO_NAME} \\"
  echo "      --location=${REGION} \\"
  echo "      --project=${GCP_PROJECT_ID}"
  echo ""
  echo "(dry-run — no changes made)"
  exit 0
fi

# Check whether the repository already exists.
if gcloud artifacts repositories describe "${REPO_NAME}" \
    --location="${REGION}" \
    --project="${GCP_PROJECT_ID}" \
    --format="value(name)" &>/dev/null; then
  echo "✔  Repository '${REPO_NAME}' already exists in ${REGION} — nothing to do."
else
  echo "➕  Creating Artifact Registry repository '${REPO_NAME}' …"
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format="${FORMAT}" \
    --location="${REGION}" \
    --description="${DESCRIPTION}" \
    --project="${GCP_PROJECT_ID}"
  echo "✔  Repository created."
fi

echo ""
echo "Repository details:"
gcloud artifacts repositories describe "${REPO_NAME}" \
  --location="${REGION}" \
  --project="${GCP_PROJECT_ID}"

echo ""
echo "Docker registry hostname:"
echo "  ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${REPO_NAME}"

# Derive the GitHub repo URL from git remote (best-effort).
GITHUB_REPO_URL=""
if command -v git &>/dev/null; then
  REMOTE_URL=$(git -C "$(dirname "$0")/.." remote get-url origin 2>/dev/null || true)
  # Convert SSH (git@github.com:org/repo.git) or HTTPS to a base HTTPS URL.
  if [[ "$REMOTE_URL" =~ ^git@github\.com:(.+)\.git$ ]]; then
    GITHUB_REPO_URL="https://github.com/${BASH_REMATCH[1]}"
  elif [[ "$REMOTE_URL" =~ ^https://github\.com/(.+?)(\.git)?$ ]]; then
    GITHUB_REPO_URL="https://github.com/${BASH_REMATCH[1]}"
  fi
fi

echo ""
echo "Next steps:"
if [[ -n "${GITHUB_REPO_URL}" ]]; then
  echo "  1. Add GCP_PROJECT_ID as a repository Variable in GitHub:"
  echo "     ${GITHUB_REPO_URL}/settings/variables/actions"
  echo "  2. Add GCP_SA_KEY as a repository Secret in GitHub:"
  echo "     ${GITHUB_REPO_URL}/settings/secrets/actions"
else
  echo "  1. Add GCP_PROJECT_ID as a repository Variable in GitHub Actions settings."
  echo "  2. Add GCP_SA_KEY as a repository Secret in GitHub Actions settings."
fi
echo "  3. Push to main (or trigger workflow_dispatch) to deploy."

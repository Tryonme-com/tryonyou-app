#!/usr/bin/env bash
# supercommit_max.sh — add/commit/push con sellos TryOnYou + checks opcionales + deploy opcional.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FAST_MODE=false
DEPLOY_MODE=false
COMMIT_MSG_RAW=""

DEFAULT_MSG="OMEGA_DEPLOY: sincronización del búnker Oberkampf (75011) con la galería web."

REQUIRED_STAMPS=(
  "@CertezaAbsoluta"
  "@lo+erestu"
  "PCT/EP2025/067317"
  "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]
  bash supercommit_max.sh "mensaje libre"

Opciones:
  --fast    omite tests/build y hace solo add+commit+push
  --deploy  tras commit/push ejecuta despliegue Vercel (requiere VERCEL_TOKEN)
  --msg     mensaje de commit base (los sellos requeridos se autoañaden si faltan)
EOF
}

append_missing_stamps() {
  local message="$1"
  local stamp=""
  for stamp in "${REQUIRED_STAMPS[@]}"; do
    if [[ "$message" != *"$stamp"* ]]; then
      message="${message} ${stamp}"
    fi
  done
  printf "%s" "$message"
}

log_step() {
  printf "\n==> %s\n" "$1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST_MODE=true
      shift
      ;;
    --deploy)
      DEPLOY_MODE=true
      shift
      ;;
    --msg)
      if [[ $# -lt 2 ]]; then
        echo "❌ --msg requiere un argumento." >&2
        usage
        exit 1
      fi
      COMMIT_MSG_RAW="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "$COMMIT_MSG_RAW" ]]; then
        COMMIT_MSG_RAW="$1"
      else
        COMMIT_MSG_RAW="$COMMIT_MSG_RAW $1"
      fi
      shift
      ;;
  esac
done

if [[ -z "$COMMIT_MSG_RAW" ]]; then
  COMMIT_MSG_RAW="$DEFAULT_MSG"
fi
FINAL_MSG="$(append_missing_stamps "$COMMIT_MSG_RAW")"

if [[ "$FAST_MODE" == false ]]; then
  log_step "Python tests"
  python3 -m unittest discover -s tests -p 'test_*.py' -v

  log_step "TypeScript type-check"
  npx tsc --noEmit

  log_step "Vite production build"
  npm run build
fi

log_step "Git add"
git add -A

committed=false
if git diff --cached --quiet; then
  echo "ℹ️  nada nuevo: sin commit."
else
  log_step "Git commit"
  git commit -m "$FINAL_MSG"
  committed=true
fi

branch_name="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$committed" == true ]]; then
  if git remote get-url origin >/dev/null 2>&1; then
    log_step "Git push"
    git push -u origin "$branch_name"
  else
    echo "ℹ️  No existe remote 'origin'; commit local completado."
  fi
fi

if [[ "$DEPLOY_MODE" == true ]]; then
  log_step "Deploy Vercel"
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ VERCEL_TOKEN no está definido." >&2
    exit 1
  fi

  if ! command -v vercel >/dev/null 2>&1; then
    npm i -g vercel@latest
  fi
  vercel deploy --prod --yes --token "$VERCEL_TOKEN"
fi

echo "✅ Supercommit_Max finalizado."
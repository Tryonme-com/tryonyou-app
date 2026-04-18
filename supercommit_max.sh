#!/usr/bin/env bash
# supercommit_max v10.18
# Commit/push soberano con sellos obligatorios y despliegue opcional.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

STAMP_C="@CertezaAbsoluta"
STAMP_L="@lo+erestu"
STAMP_P="PCT/EP2025/067317"
STAMP_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"
DEFAULT_MSG="OMEGA_DEPLOY: Sync bunker Oberkampf 75011 con galería web."

FAST_MODE=0
DEPLOY_MODE=0
CUSTOM_MSG=""

usage() {
  cat <<'EOF'
Uso:
  bash supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Opciones:
  --fast      Omite build/tests y ejecuta solo flujo git.
  --deploy    Requiere VERCEL_TOKEN y ejecuta vercel deploy --prod.
  --msg       Mensaje de commit personalizado (sellos se añaden automáticamente).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fast)
      FAST_MODE=1
      shift
      ;;
    --deploy)
      DEPLOY_MODE=1
      shift
      ;;
    --msg)
      if [[ $# -lt 2 ]]; then
        echo "Error: --msg requiere un valor." >&2
        exit 1
      fi
      CUSTOM_MSG="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      # Compatibilidad: permitir mensaje posicional.
      CUSTOM_MSG="${CUSTOM_MSG:+$CUSTOM_MSG }$1"
      shift
      ;;
  esac
done

ensure_stamp() {
  local msg="$1"
  local stamp="$2"
  if [[ "$msg" != *"$stamp"* ]]; then
    msg="$msg $stamp"
  fi
  printf '%s' "$msg"
}

COMMIT_MSG="${CUSTOM_MSG:-$DEFAULT_MSG}"
COMMIT_MSG="$(ensure_stamp "$COMMIT_MSG" "$STAMP_C")"
COMMIT_MSG="$(ensure_stamp "$COMMIT_MSG" "$STAMP_L")"
COMMIT_MSG="$(ensure_stamp "$COMMIT_MSG" "$STAMP_P")"
COMMIT_MSG="$(ensure_stamp "$COMMIT_MSG" "$STAMP_PROTOCOL")"

if [[ "$FAST_MODE" -eq 0 ]]; then
  echo ">> Ejecutando Vite production build"
  npm run build
  echo ">> Ejecutando Python tests"
  python3 -m unittest discover -s tests -p "test_*.py"
else
  echo ">> Modo --fast activo: validaciones pesadas omitidas."
fi

git add -A
COMMIT_FAILED=0
if git diff --cached --quiet; then
  echo ">> No hay nada nuevo, sin commit."
  DID_COMMIT=0
else
  if git commit -m "$COMMIT_MSG"; then
    echo ">> Commit creado con sellos de protocolo."
    DID_COMMIT=1
  else
    echo ">> Advertencia: commit bloqueado o fallido; sin commit." >&2
    DID_COMMIT=0
    COMMIT_FAILED=1
  fi
fi

if git rev-parse --verify "@{u}" >/dev/null 2>&1; then
  AHEAD_COUNT="$(git rev-list --count "@{u}..HEAD" || echo 0)"
  if [[ "${AHEAD_COUNT:-0}" -gt 0 ]]; then
    git push
    echo ">> Push ejecutado sobre upstream."
  else
    echo ">> Sin push: rama al día con upstream."
  fi
else
  echo ">> Sin upstream (@{u}): no se hace push automático."
fi

if [[ "$DEPLOY_MODE" -eq 1 ]]; then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "Error: --deploy requiere VERCEL_TOKEN en el entorno." >&2
    exit 2
  fi
  echo ">> Deploy Vercel (producción)."
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
fi

echo ">> Supercommit Max finalizado."
if [[ "$COMMIT_FAILED" -eq 1 ]]; then
  exit 2
fi
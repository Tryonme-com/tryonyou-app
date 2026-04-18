#!/usr/bin/env bash
set -euo pipefail

# supercommit_max — flujo soberano seguro para commit + push (+ deploy opcional)
# Requisitos de sello:
#   @CertezaAbsoluta @lo+erestu PCT/EP2025/067317
#   Bajo Protocolo de Soberanía V10 - Founder: Rubén

FAST_MODE=0
DEPLOY_MODE=0
CUSTOM_MSG=""
STAMP_A="@CertezaAbsoluta"
STAMP_B="@lo+erestu"
STAMP_PATENT="PCT/EP2025/067317"
STAMP_PROTOCOL="Bajo Protocolo de Soberanía V10 - Founder: Rubén"
DEFAULT_TITLE="OMEGA_DEPLOY: Supercommit Max TryOnYou"

usage() {
  cat <<'EOF'
Uso:
  ./supercommit_max.sh [--fast] [--deploy] [--msg "mensaje"]

Flags:
  --fast      Omite build y tests (útil para commits rápidos).
  --deploy    Ejecuta deploy Vercel (requiere VERCEL_TOKEN).
  --msg       Mensaje personalizado. Si faltan sellos, se autoagregan.
EOF
}

while (($# > 0)); do
  case "$1" in
    --fast)
      FAST_MODE=1
      ;;
    --deploy)
      DEPLOY_MODE=1
      ;;
    --msg)
      shift
      if (($# == 0)); then
        echo "❌ --msg requiere un valor." >&2
        usage
        exit 2
      fi
      CUSTOM_MSG="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "❌ Argumento no reconocido: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Debes ejecutar este script dentro de un repositorio git." >&2
  exit 2
fi

ensure_stamp() {
  local text="$1"
  local stamp="$2"
  if [[ "$text" == *"$stamp"* ]]; then
    printf '%s' "$text"
    return 0
  fi
  printf '%s %s' "$text" "$stamp"
}

build_commit_message() {
  local msg="${CUSTOM_MSG:-$DEFAULT_TITLE}"
  msg="$(ensure_stamp "$msg" "$STAMP_A")"
  msg="$(ensure_stamp "$msg" "$STAMP_B")"
  msg="$(ensure_stamp "$msg" "$STAMP_PATENT")"
  msg="$(ensure_stamp "$msg" "$STAMP_PROTOCOL")"
  printf '%s' "$msg"
}

COMMIT_MSG="$(build_commit_message)"

if ((FAST_MODE == 0)); then
  if [[ -f "package.json" ]]; then
    echo "▶ Vite production build"
    npm run build
  fi
  if [[ -d "tests" ]]; then
    echo "▶ Python tests"
    python3 -m unittest discover -s tests
  fi
fi

git add -A
COMMIT_CREATED=0
if git diff --cached --quiet; then
  echo "ℹ️ Nada nuevo para commit; sin commit."
else
  if git commit -m "$COMMIT_MSG"; then
    COMMIT_CREATED=1
    echo "✅ Commit creado."
  else
    echo "⚠️ Commit no creado (hook/política o validación externa)." >&2
  fi
fi

if ((COMMIT_CREATED == 1)) && git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  if git push; then
    echo "✅ Push realizado al upstream."
  else
    echo "⚠️ Push no completado." >&2
  fi
else
  echo "ℹ️ Sin upstream configurado (@{u}); omito push automático."
fi

if ((DEPLOY_MODE == 1)); then
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    echo "❌ --deploy requiere VERCEL_TOKEN." >&2
    exit 1
  fi
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
fi
#!/usr/bin/env bash
# supercommit_max.sh
# Flujo TryOnYou: validación mínima, sellado de commit y push seguro.
#
# Uso:
#   ./supercommit_max.sh
#   ./supercommit_max.sh --fast
#   ./supercommit_max.sh --msg "Mi título"
#   ./supercommit_max.sh --fast --deploy
#
# Reglas:
# - Autoañade sellos obligatorios al mensaje si faltan.
# - Hace push solo si hay commit nuevo o rama por delante del upstream.
# - --deploy exige VERCEL_TOKEN (no se guarda en código).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

FAST_MODE=0
DEPLOY_MODE=0
CUSTOM_MSG=""

DEFAULT_BASE_MSG="OMEGA_DEPLOY: sincronización búnker Oberkampf 75011 con galería web"
REQUIRED_SUFFIX="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"

print_usage() {
  cat <<'USAGE'
Uso: supercommit_max.sh [opciones]
  --fast            Omite build y tests
  --deploy          Ejecuta despliegue Vercel (requiere VERCEL_TOKEN)
  --msg "mensaje"   Mensaje de commit base
  -h, --help        Muestra esta ayuda
USAGE
}

while (($# > 0)); do
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
      if (($# < 2)); then
        echo "❌ --msg requiere un valor." >&2
        exit 1
      fi
      CUSTOM_MSG="$2"
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      if [[ -z "$CUSTOM_MSG" ]]; then
        # Compatibilidad con wrappers antiguos que pasan el mensaje como primer argumento.
        CUSTOM_MSG="$1"
        shift
      else
        echo "❌ Argumento no reconocido: $1" >&2
        print_usage >&2
        exit 1
      fi
      ;;
  esac
done

if [[ "$DEPLOY_MODE" -eq 1 && -z "${VERCEL_TOKEN:-}" ]]; then
  echo "❌ VERCEL_TOKEN es obligatorio para --deploy." >&2
  exit 1
fi

compose_message() {
  local base="$1"
  local out="$base"
  [[ -n "$out" ]] || out="$DEFAULT_BASE_MSG"
  [[ "$out" == *"@CertezaAbsoluta"* ]] || out="$out @CertezaAbsoluta"
  [[ "$out" == *"@lo+erestu"* ]] || out="$out @lo+erestu"
  [[ "$out" == *"PCT/EP2025/067317"* ]] || out="$out PCT/EP2025/067317"
  [[ "$out" == *"Bajo Protocolo de Soberanía V10"* ]] || out="$out Bajo Protocolo de Soberanía V10 - Founder: Rubén"
  [[ "$out" == *"Founder: Rubén"* ]] || out="$out Founder: Rubén"
  echo "$out"
}

MSG="$(compose_message "$CUSTOM_MSG")"

run_quality_gate() {
  if [[ "$FAST_MODE" -eq 1 ]]; then
    echo "⚡ Modo --fast activo: se omiten quality gates."
    return 0
  fi
  echo "🔍 TypeScript typecheck"
  npx tsc --noEmit
  echo "🏗️ Vite production build"
  npm run build
  echo "🧪 Python tests"
  python3 -m unittest tests.test_supercommit_max
}

push_if_needed() {
  local did_commit="$1"
  if [[ "$did_commit" -eq 1 ]]; then
    if git rev-parse --verify "@{u}" >/dev/null 2>&1; then
      echo "⬆️ Commit creado: push a upstream actual."
      git push
    else
      echo "ℹ️ Commit creado sin upstream. Ejecuta: git push -u origin <rama>"
    fi
    return 0
  fi

  if git rev-parse --verify "@{u}" >/dev/null 2>&1; then
    local ahead
    ahead="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || true)"
    ahead="${ahead:-0}"
    case "$ahead" in
      *[!0-9]*) ahead=0 ;;
    esac
    if [[ "$ahead" -gt 0 ]]; then
      echo "⬆️ Sin commit nuevo, pero rama por delante (${ahead}). Push."
      git push
    else
      echo "ℹ️ Sin push: nada nuevo y rama sincronizada."
    fi
  else
    echo "ℹ️ Sin push: no hay upstream (@{u})."
  fi
}

deploy_if_requested() {
  if [[ "$DEPLOY_MODE" -eq 0 ]]; then
    return 0
  fi
  echo "🚀 Despliegue Vercel (--deploy)"
  vercel deploy --prod --yes --token="$VERCEL_TOKEN"
}

echo "🏛️ SUPERCOMMIT_MAX iniciado."
run_quality_gate

git add -A
did_commit=0
if git diff --cached --quiet; then
  echo "ℹ️ Nada nuevo en índice (sin commit)."
else
  git commit -m "$MSG"
  did_commit=1
fi

push_if_needed "$did_commit"
deploy_if_requested

echo "✅ SUPERCOMMIT_MAX completado."
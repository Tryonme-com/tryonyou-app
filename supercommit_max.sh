#!/usr/bin/env bash
# supercommit_max.sh — Super Commit MAX TryOnYou
#
# Flujo completo: (build opcional) → add → commit con sellos → push → (deploy opcional).
#
# Sellos obligatorios en el mensaje de commit:
#   @CertezaAbsoluta  @lo+erestu  PCT/EP2025/067317
#
# Opciones:
#   -h, --help        Muestra esta ayuda.
#   -n, --dry-run     Simula el flujo sin ejecutar git, npm ni vercel.
#   -b, --build       Ejecuta "npm install && npm run build" antes del commit.
#   -d, --deploy      Ejecuta "vercel deploy --prod" tras el push (requiere VERCEL_TOKEN).
#   -f, --force       Usa "git push --force-with-lease" en lugar de push normal.
#   --                Fin de opciones; el siguiente argumento es el mensaje de commit.
#
# Push solo si:
#   1) Se hizo un commit nuevo en esta ejecución, o
#   2) La rama local va por delante del remoto (@{u}) aunque no haya habido commit nuevo.
# Si no hay upstream configurado no se hace push (evita errores en CI).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# ---------------------------------------------------------------------------
# Ayuda
# ---------------------------------------------------------------------------
_usage() {
  sed -n '/^# supercommit_max/,/^[^#]/{ /^#/{ s/^# \{0,1\}//; p } }' "$0"
  exit 0
}

# ---------------------------------------------------------------------------
# Validación de sellos TryOnYou
# ---------------------------------------------------------------------------
_commit_stamps_ok() {
  local m="$1"
  [[ "$m" == *"@CertezaAbsoluta"* ]] || { echo "❌ Falta @CertezaAbsoluta en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"@lo+erestu"* ]]       || { echo "❌ Falta @lo+erestu en el mensaje de commit." >&2; return 1; }
  [[ "$m" == *"PCT/EP2025/067317"* ]] || { echo "❌ Falta la patente PCT/EP2025/067317 en el mensaje de commit." >&2; return 1; }
  return 0
}

# ---------------------------------------------------------------------------
# Parse de opciones
# ---------------------------------------------------------------------------
DRY_RUN=0
DO_BUILD=0
DO_DEPLOY=0
FORCE_PUSH=0
MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)       _usage ;;
    -n|--dry-run)    DRY_RUN=1;  shift ;;
    -b|--build)      DO_BUILD=1; shift ;;
    -d|--deploy)     DO_DEPLOY=1; shift ;;
    -f|--force)      FORCE_PUSH=1; shift ;;
    --)              shift; MSG="${1:-}"; shift || true; break ;;
    -*)              echo "❌ Opción desconocida: $1" >&2; exit 1 ;;
    *)               MSG="$1"; shift; break ;;
  esac
done

MSG="${MSG:-Protocolo Soberanía: mirror V10 sello Divineo + fallback CSS @CertezaAbsoluta @lo+erestu PCT/EP2025/067317}"

if ! _commit_stamps_ok "$MSG"; then
  echo "   Uso: $0 [opciones] 'Mensaje @CertezaAbsoluta @lo+erestu PCT/EP2025/067317'" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Helpers: run / dryrun
# ---------------------------------------------------------------------------
_run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "🔵 [DRY-RUN] $*"
  else
    "$@"
  fi
}

# ---------------------------------------------------------------------------
# 1. Build opcional
# ---------------------------------------------------------------------------
if [ "$DO_BUILD" -eq 1 ]; then
  echo "🔨 Construyendo proyecto (npm install && npm run build)..."
  _run npm install --no-fund --no-audit
  _run npm run build
  echo "✅ Build completado."
fi

# ---------------------------------------------------------------------------
# 2. Git add + commit
# ---------------------------------------------------------------------------
_run git add -A

did_commit=0
if [ "$DRY_RUN" -eq 1 ]; then
  echo "🔵 [DRY-RUN] git commit -m \"$MSG\""
  did_commit=1
elif git diff --cached --quiet; then
  echo "ℹ️  Nada nuevo en el índice tras git add (sin commit en esta pasada)."
else
  git commit -m "$MSG"
  did_commit=1
fi

# ---------------------------------------------------------------------------
# 3. Push
# ---------------------------------------------------------------------------
_push() {
  if [ "$FORCE_PUSH" -eq 1 ]; then
    _run git push --force-with-lease
  else
    _run git push
  fi
}

if [ "$did_commit" -eq 1 ]; then
  echo "📤 Commit creado — haciendo push..."
  _push
elif git rev-parse --verify "@{u}" >/dev/null 2>&1; then
  ahead="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || true)"
  ahead="${ahead:-0}"
  case "$ahead" in
    *[!0-9]*) ahead=0 ;;
  esac
  if [ "$ahead" -gt 0 ]; then
    echo "📤 Sin commit nuevo, pero la rama va ${ahead} commit(s) por delante del remoto — haciendo push..."
    _push
  else
    echo "ℹ️  Sin push: índice sin cambios y la rama no está por delante del remoto."
  fi
else
  echo "ℹ️  Sin push: no hay upstream (@{u}). Configura tracking con 'git push -u origin <rama>' o empuja a mano."
fi

# ---------------------------------------------------------------------------
# 4. Deploy opcional a Vercel
# ---------------------------------------------------------------------------
if [ "$DO_DEPLOY" -eq 1 ]; then
  if [ "$DRY_RUN" -eq 0 ] && [ -z "${VERCEL_TOKEN:-}" ]; then
    echo "❌ ERROR: VERCEL_TOKEN no está definido. Define la variable de entorno o pásala al script." >&2
    exit 1
  fi
  echo "🚀 Desplegando a producción (vercel deploy --prod)..."
  _run vercel deploy --prod --yes --token="${VERCEL_TOKEN:-<VERCEL_TOKEN>}"
  echo "✅ Despliegue completado."
fi

echo "✅ [TryOnYou] Supercommit MAX finalizado — @CertezaAbsoluta @lo+erestu PCT/EP2025/067317"

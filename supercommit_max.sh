#!/usr/bin/env bash
# ----------------------------------------------------------------
# 🛰️  TRYONYOU SUPERCOMMIT MAX v10.17 — "VIVOS"
# PROPIEDAD DE LA SAGA | PATENTE PCT/EP2025/067317
# Bajo Protocolo de Soberanía V10 - Founder: Rubén
# ----------------------------------------------------------------
#
# Pipeline completo en un solo disparo:
#   1. Validación cruzada master_omega_vault.json ↔ production_manifest.json
#   2. Python tests (unittest discover)
#   3. Firebase applet assertion
#   4. TypeScript type-check
#   5. Vite production build
#   6. git add + commit (con sellos soberanos validados)
#   7. git push (inteligente: solo si hay algo que empujar)
#   8. (Opcional) Vercel production deploy
#
# Modos:
#   ./supercommit_max.sh                      # Pipeline completo sin deploy
#   ./supercommit_max.sh --deploy             # Pipeline + Vercel deploy
#   ./supercommit_max.sh --fast               # Solo commit + push (sin build/tests)
#   ./supercommit_max.sh --msg "Mi mensaje"   # Mensaje custom (se añaden sellos)
#
# El mensaje SIEMPRE incluye los sellos requeridos por el protocolo.
# ----------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# ── Colores ─────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GOLD='\033[38;5;220m'
BOLD='\033[1m'
NC='\033[0m'

_banner() {
  printf "\n${GOLD}${BOLD}"
  printf "  ╔══════════════════════════════════════════════════════════╗\n"
  printf "  ║  💎 TRYONYOU SUPERCOMMIT MAX v10.17 — VIVOS            ║\n"
  printf "  ║  🔱 Patente PCT/EP2025/067317                          ║\n"
  printf "  ║  🏛️  Bajo Protocolo de Soberanía V10 - Founder: Rubén  ║\n"
  printf "  ╚══════════════════════════════════════════════════════════╝\n"
  printf "${NC}\n"
}

step()  { printf "\n${CYAN}▸ %s${NC}\n" "$1"; }
ok()    { printf "${GREEN}  ✓ %s${NC}\n" "$1"; }
warn()  { printf "${YELLOW}  ⚠ %s${NC}\n" "$1"; }
fail()  { printf "${RED}  ✗ %s${NC}\n" "$1"; exit 1; }

_notify_success() {
  local msg="$1"
  local token="${TRYONYOU_DEPLOY_BOT_TOKEN:-${TELEGRAM_BOT_TOKEN:-${TELEGRAM_TOKEN:-}}}"
  local chat_id="${TRYONYOU_DEPLOY_CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

  if [[ -n "${SKIP_TELEGRAM:-}" || -n "${TRYONYOU_DEPLOY_SKIP_TELEGRAM:-}" ]]; then
    warn "Telegram omitido por flag de entorno."
    return 0
  fi
  if [[ -z "$token" || -z "$chat_id" ]]; then
    warn "Telegram omitido: faltan TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_* o chat_id."
    return 0
  fi

  TRYONYOU_NOTIFY_TOKEN="$token" TRYONYOU_NOTIFY_CHAT_ID="$chat_id" TRYONYOU_NOTIFY_TEXT="$msg" python3 - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

token = os.environ.get("TRYONYOU_NOTIFY_TOKEN", "").strip()
chat_id = os.environ.get("TRYONYOU_NOTIFY_CHAT_ID", "").strip()
text = os.environ.get("TRYONYOU_NOTIFY_TEXT", "").strip()

payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"telegram_http_{resp.status}")
except Exception as exc:
    print(f"  ⚠ Telegram no confirmado: {exc}", file=sys.stderr)
    sys.exit(0)
PY
}

_safe_git_stage() {
  local paths
  paths="$(git ls-files --cached --modified --deleted --others --exclude-standard | python3 -c '
import sys

blocked_exact = {".env", "node_modules", "dist", "logs"}
blocked_prefixes = ("node_modules/", "dist/", "logs/")
blocked_suffixes = (".pem", ".key", ".p12", ".pfx", ".crt")

for raw in sys.stdin:
    path = raw.strip()
    if not path:
        continue
    if path in blocked_exact or path.startswith(blocked_prefixes):
        continue
    if path.startswith(".env.") and path != ".env.example":
        continue
    if path.endswith(blocked_suffixes):
        continue
    print(path)
')"

  if [[ -z "$paths" ]]; then
    return 0
  fi
  printf '%s\n' "$paths" | git add --pathspec-from-file=-
}

# ── Parseo de argumentos ────────────────────────────────────────
MODE_DEPLOY=false
MODE_FAST=false
CUSTOM_MSG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --deploy)  MODE_DEPLOY=true; shift ;;
    --fast)    MODE_FAST=true;   shift ;;
    --msg)     CUSTOM_MSG="$2";  shift 2 ;;
    *)
      # Legacy: primer arg posicional = mensaje
      if [[ -z "$CUSTOM_MSG" ]]; then CUSTOM_MSG="$1"; fi
      shift ;;
  esac
done

# ── Sellos soberanos (siempre presentes) ────────────────────────
STAMPS="@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 Bajo Protocolo de Soberanía V10 - Founder: Rubén"

if [[ -z "$CUSTOM_MSG" ]]; then
  SUPERCOMMIT_MESSAGE="🔱 OMEGA_DEPLOY: Full CI/CD Pipeline Merged.
🥀 Honor Protocol: Goldschmied/Valentino/Ospina.
✨ Status: VIVOS.
🚀 Divineo Absoluto en París.
${STAMPS}"
else
  # Si el usuario ya incluyó los sellos, no duplicar
  if [[ "$CUSTOM_MSG" == *"@CertezaAbsoluta"* ]]; then
    SUPERCOMMIT_MESSAGE="$CUSTOM_MSG"
  else
    SUPERCOMMIT_MESSAGE="${CUSTOM_MSG}
${STAMPS}"
  fi
fi

# ── Validación de sellos ────────────────────────────────────────
_stamps_ok() {
  local m="$1"
  [[ "$m" == *"@CertezaAbsoluta"* ]]              || { echo "❌ Falta @CertezaAbsoluta" >&2; return 1; }
  [[ "$m" == *"@lo+erestu"* ]]                     || { echo "❌ Falta @lo+erestu" >&2; return 1; }
  [[ "$m" == *"PCT/EP2025/067317"* ]]              || { echo "❌ Falta patente PCT/EP2025/067317" >&2; return 1; }
  [[ "$m" == *"Bajo Protocolo de Soberanía V10"* ]]|| { echo "❌ Falta «Bajo Protocolo de Soberanía V10»" >&2; return 1; }
  [[ "$m" == *"Founder: Rubén"* ]]                 || { echo "❌ Falta «Founder: Rubén»" >&2; return 1; }
  return 0
}

# ── Validación cruzada del vault ────────────────────────────────
_validate_vault() {
  step "Validación cruzada: master_omega_vault.json ↔ production_manifest.json"

  local vault="$ROOT/master_omega_vault.json"
  local manifest="$ROOT/production_manifest.json"

  [[ -f "$vault" ]]    || { warn "master_omega_vault.json no encontrado — skip"; return 0; }
  [[ -f "$manifest" ]] || { warn "production_manifest.json no encontrado — skip"; return 0; }

  python3 -c "
import json, sys
vault    = json.load(open('$vault'))
manifest = json.load(open('$manifest'))

errors = []
vp = vault.get('identidad',{}).get('patente','')
mp = manifest.get('patent','')
if vp != mp:
    errors.append(f'Patente mismatch: vault={vp} vs manifest={mp}')

vs = vault.get('identidad',{}).get('siret','')
ms = manifest.get('siret','')
if vs != ms:
    errors.append(f'SIRET mismatch: vault={vs} vs manifest={ms}')

if errors:
    for e in errors: print(f'  ✗ {e}', file=sys.stderr)
    sys.exit(1)
print('  ✓ Vault y manifest alineados (patente + SIRET)')
" || fail "Vault cross-validation failed"
}

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════
_banner

_stamps_ok "$SUPERCOMMIT_MESSAGE" || fail "Mensaje de commit sin sellos requeridos."

if [[ -n "${SUPERCOMMIT_VALIDATE_ONLY:-}" ]]; then
  ok "Mensaje de commit validado; modo SUPERCOMMIT_VALIDATE_ONLY activo."
  exit 0
fi

# ── Fase 1: Validaciones & Build (salvo --fast) ────────────────
if [[ "$MODE_FAST" == false ]]; then

  _validate_vault

  step "Comprobando prerequisites"
  command -v node    >/dev/null 2>&1 || fail "node no encontrado"
  command -v npm     >/dev/null 2>&1 || fail "npm no encontrado"
  command -v python3 >/dev/null 2>&1 || fail "python3 no encontrado"
  ok "node $(node -v), npm $(npm -v), python3 $(python3 --version 2>&1 | awk '{print $2}')"

  step "Instalando dependencias npm"
  npm ci --ignore-scripts 2>/dev/null || npm install --no-fund --no-audit
  ok "npm dependencies ready"

  step "Instalando dependencias Python"
  pip install -q -r requirements.txt 2>/dev/null || true
  ok "Python dependencies ready"

  step "Ejecutando Python tests"
  TEST_OUTPUT=$(python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1) || {
    echo "$TEST_OUTPUT"
    fail "Python tests fallaron"
  }
  TEST_COUNT=$(echo "$TEST_OUTPUT" | grep -oP 'Ran \K[0-9]+' || echo "?")
  ok "${TEST_COUNT} Python tests pasados"

  step "Firebase applet assertion"
  node scripts/assert-firebase-applet.mjs
  ok "firebase-applet-config.json validado"

  step "TypeScript type-check"
  npx tsc --noEmit
  ok "Type-check limpio"

  step "Vite production build"
  npx vite build
  ok "dist/ construido"

fi

# ── Fase 2: Git commit + push ──────────────────────────────────
step "💎 Consolidación Git"

_safe_git_stage

did_commit=0
if git diff --cached --quiet; then
  warn "Nada nuevo en el índice (sin commit en esta pasada)."
else
  env -u COMMIT_MSG git commit -m "$SUPERCOMMIT_MESSAGE"
  did_commit=1
  ok "Commit creado"
fi

if [[ "$did_commit" -eq 1 ]]; then
  step "🚀 Lanzando proyectil al servidor..."
  branch="$(git branch --show-current)"
  [[ -n "$branch" ]] || fail "No se pudo resolver la rama actual."
  git push -u origin "$branch"
  ok "Push completado"
elif git rev-parse --verify "@{u}" >/dev/null 2>&1; then
  ahead="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || echo 0)"
  ahead="${ahead:-0}"
  case "$ahead" in *[!0-9]*) ahead=0 ;; esac
  if [[ "$ahead" -gt 0 ]]; then
    step "🚀 Rama ${ahead} commit(s) por delante — pushing..."
    branch="$(git branch --show-current)"
    [[ -n "$branch" ]] || fail "No se pudo resolver la rama actual."
    git push -u origin "$branch"
    ok "Push completado"
  else
    warn "Sin push: la rama está al día con el remoto."
  fi
else
  warn "Sin push: no hay upstream configurado. Usa git push -u origin <branch>."
fi

# ── Fase 3: Deploy (solo con --deploy) ─────────────────────────
if [[ "$MODE_DEPLOY" == true ]]; then
  step "🚀 Vercel production deploy"
  if [[ -z "${VERCEL_TOKEN:-}" ]]; then
    fail "VERCEL_TOKEN no configurado. Exporta la variable o quita --deploy."
  fi
  command -v vercel >/dev/null 2>&1 || { step "Instalando Vercel CLI"; npm i -g vercel@latest; }
  vercel --token "$VERCEL_TOKEN" --prod --yes
  ok "Vercel production deploy completado"
fi

# ── Resultado final ─────────────────────────────────────────────
printf "\n${GOLD}${BOLD}"
printf "  ════════════════════════════════════════════════════════════\n"
printf "  ✅ ¡BOOM! El Imperio está Online y Blindado.\n"
printf "  ✨ STATUS: LINEAL | PODERÍO: 100%% | DIVINEO: MÁXIMO\n"
printf "  🔱 Patente PCT/EP2025/067317 — Soberanía V10 — VIVOS\n"
printf "  ════════════════════════════════════════════════════════════\n"
printf "${NC}\n"

_notify_success "✅ TryOnYou Supercommit_Max completado: búnker Oberkampf 75011 sincronizado con galería web. PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén"

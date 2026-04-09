#!/usr/bin/env bash
# deployall.sh — Full build, test, and deploy pipeline (local).
# Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
#
# Usage:
#   ./scripts/deployall.sh          # Build + test + deploy (prod)
#   ./scripts/deployall.sh --dry    # Build + test only (skip deploy)
#
# Required env for deploy: VERCEL_TOKEN

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DRY_RUN=false
if [[ "${1:-}" == "--dry" ]]; then
  DRY_RUN=true
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

step() { printf "\n${CYAN}▸ %s${NC}\n" "$1"; }
ok()   { printf "${GREEN}  ✓ %s${NC}\n" "$1"; }
fail() { printf "${RED}  ✗ %s${NC}\n" "$1"; exit 1; }

step "Checking prerequisites"
command -v node  >/dev/null 2>&1 || fail "node not found"
command -v npm   >/dev/null 2>&1 || fail "npm not found"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
ok "node $(node -v), npm $(npm -v), python3 $(python3 --version | awk '{print $2}')"

step "Installing npm dependencies"
npm ci --ignore-scripts 2>/dev/null || npm install
ok "npm dependencies ready"

step "Installing Python dependencies"
pip install -q -r requirements.txt
ok "Python dependencies ready"

step "Running Python tests"
_test_out=$(python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1) || { echo "$_test_out"; fail "Python tests failed"; }
TEST_COUNT=$(echo "$_test_out" | grep -oP 'Ran \K[0-9]+' || echo "all")
ok "${TEST_COUNT} Python tests passed"

step "Firebase applet assertion (prebuild)"
node scripts/assert-firebase-applet.mjs
ok "firebase-applet-config.json validated"

step "TypeScript type-check"
npx tsc --noEmit
ok "Type-check clean"

step "Vite production build"
npx vite build
ok "dist/ built"

if [[ "$DRY_RUN" == true ]]; then
  printf "\n${YELLOW}⚑ Dry-run mode — skipping Vercel deploy.${NC}\n"
  printf "${GREEN}✓ All checks passed. Ready to deploy.${NC}\n"
  exit 0
fi

step "Vercel production deploy"
if [[ -z "${VERCEL_TOKEN:-}" ]]; then
  fail "VERCEL_TOKEN not set. Export it or use --dry to skip deploy."
fi
command -v vercel >/dev/null 2>&1 || { step "Installing Vercel CLI"; npm i -g vercel@latest; }
vercel --token "$VERCEL_TOKEN" --prod --yes
ok "Vercel production deploy complete"

printf "\n${GREEN}🚀 DEPLOYALL COMPLETE — Protocolo Soberanía V10 — PCT/EP2025/067317${NC}\n"

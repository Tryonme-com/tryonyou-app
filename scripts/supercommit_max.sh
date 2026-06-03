#!/usr/bin/env bash
# supercommit_max.sh — Full validation → auto-commit pipeline for tryonyou-app.
#
# Steps
#   1. TypeScript type-check  (corepack pnpm run check)
#   2. Production build       (corepack pnpm run build)
#   3. Python API unit tests  (python3 -m unittest discover -s tests -q)
#   4. Prettier format        (corepack pnpm run format)
#   5. git add -A
#   6. git commit  (message auto-generated from timestamp, or supplied via -m)
#   7. git push    (only when --push flag is passed)
#
# Usage
#   bash scripts/supercommit_max.sh
#   bash scripts/supercommit_max.sh -m "feat: my custom message"
#   bash scripts/supercommit_max.sh --push
#   bash scripts/supercommit_max.sh -m "fix: hotfix" --push
#   bash scripts/supercommit_max.sh --skip-build --push

set -euo pipefail

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}✔  $*${RESET}"; }
info() { echo -e "${CYAN}➤  $*${RESET}"; }
warn() { echo -e "${YELLOW}⚠  $*${RESET}"; }
fail() { echo -e "${RED}✘  $*${RESET}"; exit 1; }

# ── defaults ─────────────────────────────────────────────────────────────────
COMMIT_MSG=""
DO_PUSH=false
SKIP_BUILD=false
SKIP_TESTS=false

# ── arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message)   COMMIT_MSG="$2"; shift 2 ;;
    --push)         DO_PUSH=true;    shift   ;;
    --skip-build)   SKIP_BUILD=true; shift   ;;
    --skip-tests)   SKIP_TESTS=true; shift   ;;
    *) fail "Unknown argument: $1";;
  esac
done

# ── resolve project root (script lives in scripts/) ──────────────────────────
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo ""
echo -e "${BOLD}═══════════════════════════════════════════${RESET}"
echo -e "${BOLD}   SUPERCOMMIT MAX  —  tryonyou-app        ${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════${RESET}"
echo ""

# ── 1. TypeScript check ───────────────────────────────────────────────────────
info "Step 1/4 — TypeScript type-check"
if corepack pnpm run check; then
  ok "TypeScript: no errors"
else
  fail "TypeScript check failed. Fix errors before committing."
fi

# ── 2. Production build ───────────────────────────────────────────────────────
if [[ "$SKIP_BUILD" == "false" ]]; then
  info "Step 2/4 — Production build"
  if corepack pnpm run build; then
    ok "Build: success"
  else
    fail "Build failed. Fix errors before committing."
  fi
else
  warn "Step 2/4 — Production build SKIPPED (--skip-build)"
fi

# ── 3. Python API tests ───────────────────────────────────────────────────────
if [[ "$SKIP_TESTS" == "false" ]]; then
  info "Step 3/4 — Python API unit tests"
  if python3 -m unittest discover -s tests -q 2>&1; then
    ok "Python tests: all passed"
  else
    fail "Python tests failed. Fix failing tests before committing."
  fi
else
  warn "Step 3/4 — Python tests SKIPPED (--skip-tests)"
fi

# ── 4. Prettier format ────────────────────────────────────────────────────────
info "Step 4/4 — Prettier format"
if corepack pnpm run format; then
  ok "Formatting applied"
else
  warn "Prettier had warnings (non-blocking)"
fi

# ── 5 & 6. Stage + commit ──────────────────────────────────────────────────────
echo ""
info "Staging all changes…"
git add -A

if git diff --cached --quiet; then
  warn "Nothing to commit — working tree is clean."
  echo ""
  exit 0
fi

# Auto-generate message if none supplied
if [[ -z "$COMMIT_MSG" ]]; then
  TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
  COMMIT_MSG="chore: supercommit [${TIMESTAMP}]"
fi

info "Committing: \"${COMMIT_MSG}\""
git commit -m "$COMMIT_MSG"
ok "Commit created."

# ── 7. Optional push ─────────────────────────────────────────────────────────
if [[ "$DO_PUSH" == "true" ]]; then
  BRANCH=$(git symbolic-ref --short HEAD)
  info "Pushing branch '${BRANCH}' to origin…"
  git push origin "$BRANCH"
  ok "Pushed to origin/${BRANCH}."
else
  warn "Not pushing (pass --push to push automatically)."
fi

echo ""
echo -e "${GREEN}${BOLD}All done. Commit ready.${RESET}"
echo ""

#!/usr/bin/env bash
# Supercommit máximo: add, commit con sellos TryOnYou, push.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

MSG="${1:-Protocolo Soberanía: mirror V10 sello Divineo + fallback CSS @CertezaAbsoluta @lo+erestu PCT/EP2025/067317}"

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit. Skipping push (no new commit in this run)."
else
  git commit -m "$MSG"
  git push
fi

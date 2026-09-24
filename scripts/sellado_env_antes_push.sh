#!/usr/bin/env bash
# Quita .env del índice si se trackeó por error; NO hace `git add .`.
# Commit/push manual con mensaje Pau (@CertezaAbsoluta, patente, protocolo V10).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! grep -qE '^\.env$' .gitignore 2>/dev/null; then
  echo "Añadiendo .env a .gitignore"
  printf '\n.env\n' >> .gitignore
fi

# Dejar de trackear ficheros de entorno si alguna vez se indexaron
for f in .env .env.local .env.production.local; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    git rm --cached -f "$f" 2>/dev/null || true
    echo "Quitado del índice: $f"
  fi
done

git add .gitignore

echo ""
echo "OK: .gitignore actualizado y cache de .env limpiada si aplicaba."
echo "Siguiente paso (manual): revisa 'git status', añade solo rutas necesarias (no 'git add .'),"
echo "commit con sellos Pau y push. Ej.: git_protocol_bunker_safe.py con BUNKER_GIT_PATHS."

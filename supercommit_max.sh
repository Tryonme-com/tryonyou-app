#!/usr/bin/env bash
# Supercommit_Max TryOnYou: build + git add/commit/push en la rama actual.
# Uso:
#   ./supercommit_max.sh "Mensaje opcional"
#
# Variables opcionales:
#   SUPERCOMMIT_SKIP_BUILD=1    -> omite npm run build
#   SUPERCOMMIT_DRY_RUN=1       -> no hace git push
#   SUPERCOMMIT_SKIP_NOTIFY=1   -> no notifica al bot
#   SUPERCOMMIT_SYNC_NODE=75011 -> nodo de sincronizacion (default 75011)
#   SUPERCOMMIT_SYNC_LABEL=Oberkampf
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SYNC_NODE="${SUPERCOMMIT_SYNC_NODE:-75011}"
SYNC_LABEL="${SUPERCOMMIT_SYNC_LABEL:-Oberkampf}"

DEFAULT_MSG="Supercommit_Max: sincronizacion bunker ${SYNC_LABEL} (${SYNC_NODE}) con galeria web."
COMMIT_MSG="${1:-$DEFAULT_MSG}"

for required in "@CertezaAbsoluta" "@lo+erestu" "PCT/EP2025/067317" "Bajo Protocolo de Soberanía V10 - Founder: Rubén"; do
  if [[ "$COMMIT_MSG" != *"$required"* ]]; then
    COMMIT_MSG+=" $required"
  fi
done

echo "==> Supercommit_Max en rama: $BRANCH"
echo "==> Sincronizando nodo ${SYNC_LABEL} (${SYNC_NODE})"

if [[ "${SUPERCOMMIT_SKIP_BUILD:-0}" != "1" && -f "$ROOT/package.json" ]]; then
  echo "==> Build de galeria web (npm run build)"
  npm run build
else
  echo "==> Build omitido (SUPERCOMMIT_SKIP_BUILD=1 o package.json ausente)"
fi

echo "==> Validando wrappers bash"
bash -n "$ROOT/supercommit_max.sh" "$ROOT/percommit_max.sh" "$ROOT/TRYONYOU_SUPERCOMMIT_MAX.sh"

git add -A
if git diff --cached --quiet; then
  echo "==> No hay cambios para commit."
else
  git commit -m "$COMMIT_MSG"
fi

if [[ "${SUPERCOMMIT_DRY_RUN:-0}" == "1" ]]; then
  echo "==> SUPERCOMMIT_DRY_RUN=1, push omitido."
  exit 0
fi

git push -u origin "$BRANCH"

if [[ "${SUPERCOMMIT_SKIP_NOTIFY:-0}" != "1" && -f "$ROOT/scripts/notify_tryonyou_deploy_bot.py" ]]; then
  if ! python3 "$ROOT/scripts/notify_tryonyou_deploy_bot.py" \
    --event "supercommit_max" \
    --status "success" \
    --detail "Rama ${BRANCH} sincronizada con bunker ${SYNC_LABEL} (${SYNC_NODE})."; then
    echo "==> Aviso: notificacion al bot no completada; push ya realizado."
  fi
fi

echo "==> Supercommit_Max completado."
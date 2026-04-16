#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-deploy}"

echo "🏛️ TryOnYou Hito 2 | Stripe + Sello Antracita"
echo "📌 Comando one-click (modo=${MODE})"

if [[ "${MODE}" == "dry-run" ]]; then
  exec python3 "${SCRIPT_DIR}/orquestador_hito2_stripe_antracita.py" --dry-run
fi

exec python3 "${SCRIPT_DIR}/orquestador_hito2_stripe_antracita.py" --deploy

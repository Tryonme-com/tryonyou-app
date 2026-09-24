#!/usr/bin/env bash
# Reemplazo seguro del "supercommit" bash: sin sed frágil, sin git add ., sin secretos.
# Delega en construir_bunker_comercial.py (git solo con E50_GIT_PUSH=1).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export E50_PROJECT_ROOT="${E50_PROJECT_ROOT:-$HOME/Projects/22TRYONYOU}"

echo "🚀 Sellado seguro del búnker (Python + git acotado)..."
echo "   ROOT=$E50_PROJECT_ROOT"
echo "   Para git: export E50_GIT_PUSH=1  (opcional: E50_FORCE_PUSH=1)"

python3 "$SCRIPT_DIR/construir_bunker_comercial.py"

echo "✅ Archivos generados. Cobro real: Stripe + Vercel + validación en backend."

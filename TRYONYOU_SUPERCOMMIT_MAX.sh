#!/usr/bin/env bash
# TRYONYOU — wrapper Agente 70: delega en supercommit_max (sellos + push).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

#!/usr/bin/env bash
# TRYONYOU — wrapper legacy: delega en supercommit_max (rama activa + staging seguro).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

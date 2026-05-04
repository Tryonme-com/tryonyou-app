#!/usr/bin/env bash
# TRYONYOU — wrapper legado: usa el Supercommit_Max seguro de la rama actual.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

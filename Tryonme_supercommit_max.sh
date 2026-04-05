#!/usr/bin/env bash
# Tryonme — wrapper principal: delega en supercommit_max (sellos + push).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

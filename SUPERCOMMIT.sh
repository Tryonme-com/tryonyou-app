#!/usr/bin/env bash
# Wrapper legado: delega en supercommit_max.sh para stage seguro, sellos y push a la rama actual.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

#!/usr/bin/env bash
# Wrapper seguro: nunca empuja a main; delega en la rama activa.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

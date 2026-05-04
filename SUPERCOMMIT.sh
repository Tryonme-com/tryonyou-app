#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[SUPERCOMMIT] Delegando en supercommit_max.sh sobre la rama activa."
exec "$ROOT/supercommit_max.sh" "$@"

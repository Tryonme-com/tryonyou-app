#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[SUPERCOMMIT] Delegando en Supercommit_Max seguro."
exec "$ROOT/supercommit_max.sh" "$@"

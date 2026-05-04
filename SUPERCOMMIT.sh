#!/usr/bin/env bash
# Wrapper histórico: el flujo seguro vive en supercommit_max.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

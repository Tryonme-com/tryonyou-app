#!/usr/bin/env bash
# Wrapper historico seguro: sin instalacion forzada, staging amplio ni push a main.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

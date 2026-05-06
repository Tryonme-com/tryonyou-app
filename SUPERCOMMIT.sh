#!/usr/bin/env bash
# Wrapper legacy seguro: delega en supercommit_max.sh sin push a main ni deploy forzado.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

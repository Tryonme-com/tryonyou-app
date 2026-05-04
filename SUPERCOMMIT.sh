#!/usr/bin/env bash
# Wrapper legacy: mantiene el nombre histórico sin empujar a main ni usar `git add .`.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

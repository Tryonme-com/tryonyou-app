#!/usr/bin/env bash
# Wrapper historico seguro: no instala dependencias, staging acotado y sin force-push a main.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

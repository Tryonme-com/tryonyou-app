#!/usr/bin/env bash
# TRYONYOU — wrapper Agente 70: delega en Supercommit_Max (sellos + push seguro).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/Supercommit_Max" "$@"

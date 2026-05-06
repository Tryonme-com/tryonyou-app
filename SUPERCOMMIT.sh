#!/usr/bin/env bash
# TRYONYOU — wrapper legacy seguro: delega en supercommit_max (staging blindado,
# sellos obligatorios y push no destructivo a la rama activa).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

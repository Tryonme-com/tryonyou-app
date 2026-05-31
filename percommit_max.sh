#!/usr/bin/env bash
# percommit_max — delega en supercommit_max.sh (add + commit con sellos TryOnYou + push).
# Uso: ./percommit_max.sh 'Mensaje @CertezaAbsoluta @lo+erestu PCT/EP2025/067317'
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/supercommit_max.sh" "$@"

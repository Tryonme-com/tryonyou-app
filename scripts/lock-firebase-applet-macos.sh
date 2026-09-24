#!/usr/bin/env bash
# Marca firebase-applet-config.json como inmutable en macOS (aborra borrados accidentales locales).
# Desbloqueo: chflags nouchg firebase-applet-config.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -f firebase-applet-config.json ]]; then
  echo "No existe firebase-applet-config.json" >&2
  exit 1
fi
chflags uchg firebase-applet-config.json
echo "OK: uchg aplicado a firebase-applet-config.json"

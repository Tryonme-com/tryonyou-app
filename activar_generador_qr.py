"""
Escribe src/lib/utils/qrGenerator.ts (QR cabina; base URL vía VITE_PUBLIC_APP_URL).

En el frontend: npm install qrcode && npm install -D @types/qrcode

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 activar_generador_qr.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

QR_GENERATOR_TS = r"""import QRCode from "qrcode";

function trimTrailingSlash(u: string): string {
  return u.replace(/\/$/, "");
}

const baseUrl =
  (import.meta.env.VITE_PUBLIC_APP_URL
    ? trimTrailingSlash(import.meta.env.VITE_PUBLIC_APP_URL)
    : null) ?? "https://tryonyou-app.vercel.app";

export async function generateCabineQR(prendaId: string): Promise<string | null> {
  try {
    const url = `${baseUrl}/reserve?item=${encodeURIComponent(prendaId)}`;
    const qrData = await QRCode.toDataURL(url);
    console.log("QR generado para cabina:", prendaId);
    return qrData;
  } catch (err) {
    console.error("Error generando QR", err);
    return null;
  }
}
"""


def activar_generador_qr() -> int:
    print("Paso 43: Sincronizando generador de QR para probadores...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    util = os.path.join(ROOT, "src", "lib", "utils")
    os.makedirs(util, exist_ok=True)
    path = os.path.join(util, "qrGenerator.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(QR_GENERATOR_TS)

    print(f"OK {os.path.relpath(path, ROOT)}")
    print("Instala qrcode + @types/qrcode en el proyecto Vite/React.")
    return 0


if __name__ == "__main__":
    sys.exit(activar_generador_qr())

"""
Escribe src/utils/interceptor.ts (heurística cliente: referrer / query).

Solo orientación UX; no es control de acceso (fácil de falsificar).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 interceptor_paris_hq.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

INTERCEPTOR_TS = """/**
 * Heurística en cliente (LinkedIn referrer o ?priority=high). No sustituye auth ni pagos.
 */
export function checkHighTicketInterest(): void {
  if (typeof document === "undefined" || typeof window === "undefined") {
    return;
  }
  const referrer = document.referrer ?? "";
  const search = window.location.search ?? "";
  const isCorporate =
    referrer.includes("linkedin.com") || search.includes("priority=high");

  if (isCorporate) {
    console.log(
      "Cliente de alto valor detectado. Activando flujo Enterprise 98k.",
    );
    document.body.classList.add("enterprise-mode");
  }
}
"""


def interceptor_paris_hq() -> int:
    print("🗼 Paso 42: Configurando interceptor de sedes en París...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    util = os.path.join(ROOT, "src", "utils")
    os.makedirs(util, exist_ok=True)
    path = os.path.join(util, "interceptor.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(INTERCEPTOR_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(interceptor_paris_hq())

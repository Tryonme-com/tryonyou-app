"""
CEO Agente 70 — auditoría de la columna vertebral (manifest → API → front → build).

Ejecutar: python3 agente70_columna_vertebral.py

Salida: consola + AGENTE70_VERTEBRAL_AUDIT.json en la raíz del repo.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "AGENTE70_VERTEBRAL_AUDIT.json"


@dataclass
class SpinePoint:
    id: str
    titulo: str
    ok: bool
    detalle: str


def _exists(rel: str) -> bool:
    return (ROOT / rel).is_file() or (ROOT / rel).is_dir()


def _load_manifest() -> dict:
    p = ROOT / "production_manifest.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def auditar_columna() -> list[SpinePoint]:
    m = _load_manifest()
    patent = m.get("patent", "PCT/EP2025/067317")
    points: list[SpinePoint] = []

    points.append(
        SpinePoint(
            "1",
            "Manifiesto producción (production_manifest.json)",
            _exists("production_manifest.json"),
            f"patente en JSON: {m.get('patent', '—')}",
        )
    )
    points.append(
        SpinePoint(
            "2",
            "Vault soberano (master_omega_vault.json)",
            _exists("master_omega_vault.json"),
            "fuente narrativa / LOI",
        )
    )
    points.append(
        SpinePoint(
            "3",
            "Firebase applet (prebuild)",
            _exists("firebase-applet-config.json"),
            "projectId debe coincidir con assert-firebase-applet.mjs",
        )
    )
    points.append(
        SpinePoint(
            "4",
            "API Flask — rutas financieras Stripe FR",
            _exists("api/index.py")
            and _exists("api/stripe_inauguration.py")
            and _exists("api/stripe_webhook_fr.py")
            and _exists("stripe_fr_resolve.py"),
            "/api/stripe_inauguration_checkout + /api/stripe_webhook_fr",
        )
    )
    points.append(
        SpinePoint(
            "5",
            "Fit-AI Assistant (Live It ↔ biométrico)",
            _exists("api/fit_ai_assistant.py"),
            "GET /api/fit_ai_health — env LIVEIT_DRIVE_COLLECTION_FOLDER_ID",
        )
    )
    points.append(
        SpinePoint(
            "6",
            "Front Divineo V11 + Pau tiempo real",
            _exists("src/App.tsx")
            and _exists("src/divineo/divineoV11Config.ts")
            and _exists("src/components/RealTimeAvatar.tsx")
            and _exists("src/divineo/pauV11/loadPauMasterModel.ts"),
            "RealTimeAvatar + GLB /fallback vídeo",
        )
    )
    points.append(
        SpinePoint(
            "7",
            "Tipos Vite (import.meta.env)",
            _exists("src/vite-env.d.ts"),
            "evita TS2307 en IDE",
        )
    )
    points.append(
        SpinePoint(
            "8",
            "Checkout soberano (abvetos / envBootstrap)",
            _exists("src/divineo/envBootstrap.ts")
            and _exists("src/lib/lafayetteCheckout.ts"),
            "EUR / Paris",
        )
    )
    points.append(
        SpinePoint(
            "9",
            "Orquestador async purga V11 (opcional CI local)",
            _exists("protocolo_purga_v11_async.py"),
            "python3 protocolo_purga_v11_async.py",
        )
    )
    points.append(
        SpinePoint(
            "10",
            "Equipo / mesa (referencia)",
            True,
            "mesa_redonda_omega.py, mesa_agente70_vercel_telegram.py — dominios y Telegram",
        )
    )

    _ = patent
    return points


def main() -> int:
    print("=== CEO AGENTE 70 — COLUMNA VERTEBRAL ===\n")
    pts = auditar_columna()
    ok_all = True
    for p in pts:
        estado = "OK " if p.ok else "FALTA"
        ok_all = ok_all and p.ok
        print(f"[{p.id}] {estado} — {p.titulo}")
        print(f"    {p.detalle}\n")

    report = {
        "agent": "AGENTE70",
        "columna_ok": ok_all,
        "puntos": [asdict(x) for x in pts],
        "siguiente_paso_equipo": [
            "Completar LIVEIT_DRIVE_* + GOOGLE_APPLICATION_CREDENTIALS en Vercel/servidor",
            "Subir pau_v11_high_poly.glb a public/assets/models/",
            "Registrar webhook Stripe FR → /api/stripe_webhook_fr",
            "Commit con mensaje Pau: @CertezaAbsoluta @lo+erestu PCT/EP2025/067317",
        ],
    }
    OUT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Informe escrito: {OUT_JSON.name}")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())

"""
SACMUSEUM Empire — Soberanía económica V10 (75001).
 
Sede: 27 Rue de Argenteuil, 75001 Paris · SIREN 943 610 196 · PCT/EP2025/067317.

Módulos:
  SacMuseumCore      — red de franquicias, cuota de entrada 98 000 €/nodo
  LafayetteKillSwitch — motor V10 bloqueado si setup 7 500 € ≠ PAID
  RelicValue         — archivo (piel técnica) vs oro, factor Divineo 1,5× archivo
  SacMuseumEventLogger — 4 eventos anuales obligatorios por código postal

Variable de entorno (producción / CI):
  LAFAYETTE_SETUP_FEE_STATUS=PAID  — libera el kill-switch sin llamar a .release()
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

HQ = "27 Rue de Argenteuil, 75001 Paris"
SIREN = "943 610 196"
PATENTE = "PCT/EP2025/067317"
FRANCHISE_ENTRY_EUR = 98_000.0
SETUP_FEE_EUR = 7_500.0
DIVINEO_FACTOR_ARCHIVE = 1.5
DIVINEO_FACTOR_STANDARD = 1.2
ARCHIVE_RELIC_TYPES = frozenset(
    {"Birkin_Archive", "Loewe_Vintage", "Divineo_Archive", "Hermes_Archive", "Chanel_Archive"}
)
EVENTS_ANNUAL_PER_NODE = 4


def _empire_base_dir() -> Path:
    return Path(__file__).resolve().parent


@dataclass
class SacMuseumCore:
    """Validación territorial: un nodo exige cuota Divineo Standard ≥ 98 000 €."""

    hq: str = HQ
    siren: str = SIREN
    franchise_fee: float = FRANCHISE_ENTRY_EUR
    nodes: dict[str, dict] = field(default_factory=dict)

    def register_franchise_node(self, codigo_postal: str, inversion_eur: float) -> dict:
        cp = str(codigo_postal).strip()
        if inversion_eur < self.franchise_fee:
            self.nodes[cp] = {
                "status": "PENDING_PAYMENT",
                "type": "SACMUSEUM_NODE",
                "required_eur": self.franchise_fee,
                "paid_eur": inversion_eur,
            }
            return {
                "ok": False,
                "status": "PENDING_PAYMENT",
                "message": (
                    f"❌ Cuota insuficiente en {cp} ({inversion_eur:.0f} € < "
                    f"{self.franchise_fee:.0f} € Divineo Standard)."
                ),
            }
        self.nodes[cp] = {
            "status": "ACTIVO",
            "type": "SACMUSEUM_NODE",
            "events_annual": EVENTS_ANNUAL_PER_NODE,
            "armoire_solidaire": True,
        }
        return {
            "ok": True,
            "status": "ACTIVO",
            "message": f"✅ Nodo SACMUSEUM activado en {cp}. Soberanía confirmada.",
        }


class LafayetteKillSwitch:
    """
    Setup Lafayette 7 500 €: hasta estado PAID el motor V10 queda BLOCKED.
    En runtime serverless, preferir LAFAYETTE_SETUP_FEE_STATUS=PAID.
    """

    def __init__(
        self,
        setup_fee_eur: float = SETUP_FEE_EUR,
        initial_status: str | None = None,
    ) -> None:
        self.setup_fee_eur = setup_fee_eur
        env = (os.getenv("LAFAYETTE_SETUP_FEE_STATUS", "") or "").strip().upper()
        self._status = (initial_status or env or "PENDING").strip().upper()

    @property
    def status(self) -> str:
        return self._status

    def release(self, token: str) -> None:
        """Desarmar kill-switch (p. ej. token literal 'PAID' tras confirmación tesorería)."""
        if str(token).strip().upper() == "PAID":
            self._status = "PAID"

    def audit(self) -> dict:
        paid = self._status == "PAID"
        deadline = datetime.now() + timedelta(hours=24)
        if not paid:
            return {
                "status": "DENIED",
                "lafayette": "🔴 SETUP PENDIENTE",
                "message": (
                    f"⚠️ Setup Fee {self.setup_fee_eur:.0f} € no en PAID. "
                    f"Ventana de bloqueo referencia: {deadline.isoformat(timespec='seconds')}"
                ),
                "engine_v10": "BLOCKED",
                "setup_fee_eur": self.setup_fee_eur,
            }
        return {
            "status": "OK",
            "lafayette": "🟢 PAID",
            "message": "💰 Pago Lafayette confirmado. Motor V10 Omega LIBERADO.",
            "engine_v10": "LIBERATED",
            "setup_fee_eur": self.setup_fee_eur,
        }


class RelicValue:
    """Valoración Divineo: gramo de activo de archivo frente a cotización oro."""

    @staticmethod
    def divineo_euro_per_gram_leather(gold_spot_eur_per_gram: float) -> float:
        """Precio referencia archivo = oro × 1,5 (factor Divineo acordado)."""
        return float(gold_spot_eur_per_gram) * DIVINEO_FACTOR_ARCHIVE

    @staticmethod
    def estimate_total_eur(
        tipo_pieza: str, peso_gramos: float, precio_oro_gramo: float
    ) -> tuple[float, float]:
        factor = (
            DIVINEO_FACTOR_ARCHIVE
            if tipo_pieza in ARCHIVE_RELIC_TYPES
            else DIVINEO_FACTOR_STANDARD
        )
        total = float(peso_gramos) * float(precio_oro_gramo) * factor
        return total, factor


class SacMuseumEventLogger:
    """Persiste las 4 fiestas anuales por código postal (obligatorio por nodo activo)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or _empire_base_dir() / "leads_empire").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_cp(self, codigo_postal: str) -> Path:
        safe = "".join(c for c in codigo_postal if c.isalnum() or c in "-_") or "unknown"
        return self.base_dir / f"SACMUSEUM_EVENTS_{safe}.json"

    def log_annual_event(
        self,
        codigo_postal: str,
        event_label: str,
        *,
        meta: dict | None = None,
    ) -> dict:
        path = self._path_for_cp(codigo_postal)
        existing: list[dict] = []
        if path.is_file():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    existing = raw
            except (OSError, json.JSONDecodeError):
                existing = []
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "codigo_postal": str(codigo_postal).strip(),
            "label": event_label,
            "meta": meta or {},
        }
        existing.append(entry)
        path.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        year_events = [e for e in existing if e.get("label")]
        return {
            "path": str(path),
            "events_recorded_total": len(year_events),
            "last": entry,
        }


def run_sacmuseum_sovereignty(
    *,
    kill_switch: LafayetteKillSwitch | None = None,
) -> dict:
    """
    Punto de entrada para orchestrator_v10_final.py — informe de soberanía económica.
    """
    core = SacMuseumCore()
    ks = kill_switch or LafayetteKillSwitch()
    audit = ks.audit()

    print("\n======== SACMUSEUM · Soberanía económica V10 ========")
    print(f"HQ: {HQ} | SIREN: {SIREN} | {PATENTE}")
    print(f"Kill-switch Lafayette: {audit.get('lafayette', '')}")
    print(f"engine_v10 → {audit.get('engine_v10', '')}")
    print(audit.get("message", ""))

    r75005 = core.register_franchise_node("75005", FRANCHISE_ENTRY_EUR)
    print(r75005.get("message", r75005))

    logger = SacMuseumEventLogger()
    for season in (
        "Printemps sacré",
        "Bal d’or",
        "Reliquias à l’honneur",
        "Clôture bienfaisance",
    ):
        info = logger.log_annual_event("75005", season, meta={"block": "SACMUSEUM"})
        print(f"  [events] {season} → {info['events_recorded_total']} reg. ({info['path']})")

    total, fac = RelicValue.estimate_total_eur("Loewe_Vintage", 600.0, 65.40)
    print(
        f"RelicValue (Loewe_Vintage, 600 g, oro 65,40 €/g, ×{fac}): {total:,.2f} €"
    )
    print("=======================================================\n")

    return {
        "audit": audit,
        "sample_node": r75005,
        "relic_loewe_vintage_eur": total,
        "patente": PATENTE,
        "siren": SIREN,
    }


class SacMuseumEmpire:
    """Fachada compacta compatible con demos anteriores (`python3 sacmuseum_empire.py`)."""

    def __init__(self) -> None:
        self._core = SacMuseumCore()
        self._ks = LafayetteKillSwitch()
        self.hq = self._core.hq
        self.siren = self._core.siren
        self.google_id = "111585800085885235552"
        self.franchise_fee = self._core.franchise_fee
        self.setup_fee_pending = SETUP_FEE_EUR
        self.refs_digitalizadas = 310
        self.active_nodes = self._core.nodes

    def registrar_franquicia(self, codigo_postal: str, inversion: float) -> str:
        out = self._core.register_franchise_node(codigo_postal, inversion)
        return str(out.get("message", ""))

    def check_lafayette_payment(self, paid: bool = False) -> dict | str:
        if paid:
            self._ks.release("PAID")
            return str(self._ks.audit().get("message", ""))
        audit = self._ks.audit()
        if audit.get("engine_v10") == "BLOCKED":
            return {
                "status": "WARNING",
                "message": str(audit.get("message", "")),
                "engine_v10": "RESTRICTED",
            }
        return str(audit.get("message", ""))

    def valoracion_reliquia(
        self, tipo_pieza: str, peso_gramos: float, precio_oro_gramo: float
    ) -> str:
        total, fac = RelicValue.estimate_total_eur(
            tipo_pieza, peso_gramos, precio_oro_gramo
        )
        return (
            f"💎 Activo {tipo_pieza}: Valoración Divineo de {total:.2f}€ "
            f"(factor {fac}). (Superior al Oro)."
        )


if __name__ == "__main__":
    run_sacmuseum_sovereignty()

    empire = SacMuseumEmpire()
    status_nicolas = empire.check_lafayette_payment(paid=False)
    if isinstance(status_nicolas, dict):
        print(status_nicolas["message"])
    else:
        print(status_nicolas)
    print(empire.registrar_franquicia("75005", 98_000.0))
    print(empire.valoracion_reliquia("Loewe_Vintage", 600, 65.40))

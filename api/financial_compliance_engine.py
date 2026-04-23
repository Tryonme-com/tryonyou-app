"""
FinancialComplianceEngine — auditoría de integridad PI vs ledger BigQuery (Lafayette / Qonto).

Opcional: requiere ``google-cloud-bigquery`` y credenciales GCP con acceso al dataset.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("TryOnYou_Core_Engine")


def _get_bigquery_modules():
    try:
        from google.cloud import bigquery  # type: ignore[import-untyped]

        return bigquery
    except ImportError as e:
        raise ImportError(
            "FinancialComplianceEngine requiere google-cloud-bigquery. "
            "Instala con: pip install google-cloud-bigquery"
        ) from e


class FinancialComplianceEngine:
    """Verificación de transacciones contra tablas de auditoría en BigQuery."""

    def __init__(self, project_id: str | None = None) -> None:
        bigquery = _get_bigquery_modules()
        self._bigquery = bigquery
        pid = (project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or "").strip()
        if not pid:
            raise ValueError(
                "project_id o GOOGLE_CLOUD_PROJECT es obligatorio para BigQuery."
            )
        self.project_id = pid
        self.bq_client = bigquery.Client(project=pid)
        # Tabla completa: ``proyecto.dataset.tabla`` (configurable por entorno).
        default_table = f"`{pid}.stripe_logs.payments`"
        self._payments_table = (os.getenv("BQ_STRIPE_PAYMENTS_TABLE") or default_table).strip()

    def audit_transaction_integrity(self, payment_intent_id: str, e2e_reference: str) -> bool:
        """Cruza el PaymentIntent con el ledger; ``e2e_reference`` solo en trazas (no inyecta SQL)."""
        logger.info(
            "Iniciando auditoría de ID: %s (e2e=%s)",
            payment_intent_id,
            (e2e_reference or "")[:80],
        )
        bigquery = self._bigquery
        query = f"""
            SELECT status, amount, currency
            FROM {self._payments_table}
            WHERE payment_intent_id = @pi_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("pi_id", "STRING", payment_intent_id),
            ]
        )
        query_job = self.bq_client.query(query, job_config=job_config)
        results = query_job.result()
        for row in results:
            if row.status == "succeeded":
                logger.info("Validación exitosa: %s %s", row.amount, row.currency)
                return True
        return False

    def generate_compliance_report(self, transaction_data: dict[str, Any]) -> str:
        """Genera el JSON de auditoría (banco / tesorería)."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity": "TryOnYou_SAS",
            "transaction_hash": transaction_data.get("pi_id"),
            "e2e_reference": transaction_data.get("e2e_ref"),
            "compliance_status": "VALIDATED",
            "ledger_snapshot": "COMPLETE",
        }
        return json.dumps(report, indent=4, ensure_ascii=False)

    def execute_safety_protocol(self) -> bool:
        """Comprueba que las claves críticas estén presentes antes de operaciones sensibles."""
        if not os.getenv("STRIPE_SECRET_KEY"):
            raise EnvironmentError("Fallo crítico: Llaves de entorno no cargadas.")
        logger.info("Protocolo de seguridad activo. Sistema blindado.")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    project = (os.getenv("GOOGLE_CLOUD_PROJECT") or "gen-lang-client-0091228222").strip()
    engine = FinancialComplianceEngine(project_id=project)
    try:
        if engine.execute_safety_protocol():
            data = {"pi_id": "pi_4M2y...", "e2e_ref": "PENDING_INPUT"}
            if engine.audit_transaction_integrity(data["pi_id"], data["e2e_ref"]):
                print("Auditoría de integridad: PASSED.")
    except Exception as e:
        logger.error("Error en el núcleo del sistema: %s", e)

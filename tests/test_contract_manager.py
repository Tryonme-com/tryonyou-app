from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from logic.contract_manager import ContractSovereignty


class TestContractSovereignty(unittest.TestCase):
    def test_historical_debt_total(self) -> None:
        sovereign = ContractSovereignty()
        self.assertEqual(sovereign.deuda_acumulada, 133500.00)

    def test_activation_requires_new_settlement_when_offer_expired(self) -> None:
        sovereign = ContractSovereignty()
        message = sovereign.check_activation_requirements()
        self.assertEqual(
            message,
            "OFERTA EXPIRADA. Nueva liquidación requerida: 251,500.00€. "
            "No se aceptan términos anteriores.",
        )

    def test_returns_none_when_offer_not_expired(self) -> None:
        sovereign = ContractSovereignty()
        sovereign.oferta_anual_caducada = False
        self.assertIsNone(sovereign.check_activation_requirements())


if __name__ == "__main__":
    unittest.main()

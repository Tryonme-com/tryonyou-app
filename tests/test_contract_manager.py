from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from logic.contract_manager import ContractSovereignty


class TestContractSovereignty(unittest.TestCase):
    def test_requires_env_amount_when_unconfigured(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            sovereign = ContractSovereignty()
            message = sovereign.check_activation_requirements()
        self.assertIn("CONTRACT_ACTIVATION_AMOUNT_EUR", message or "")

    def test_returns_none_when_amount_configured(self) -> None:
        with patch.dict(os.environ, {"CONTRACT_ACTIVATION_AMOUNT_EUR": "7500"}):
            sovereign = ContractSovereignty()
            self.assertIsNone(sovereign.check_activation_requirements())


if __name__ == "__main__":
    unittest.main()

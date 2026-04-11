"""
Compat shim for tooling that references `stripe-handler.py`.

Canonical implementation lives in `stripe_handler.py`.
"""

from stripe_handler import (  # noqa: F401
    LIVE_MODE,
    TEST_MODE,
    create_financial_connections_session,
    select_financial_connections_credentials,
)

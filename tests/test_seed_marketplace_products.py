"""
Tests for scripts/seed_marketplace_products.py

MongoDB interaction is fully mocked so the suite runs without a live server.
"""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure repo root is on sys.path
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import scripts.seed_marketplace_products as seed_mod
from scripts.seed_marketplace_products import MARKETPLACE_PRODUCTS, seed_products


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    """Run a coroutine synchronously in a new event loop."""
    return asyncio.run(coro)


def _make_mock_client(inserted_count: int = len(MARKETPLACE_PRODUCTS)):
    """Build a fully-mocked AsyncIOMotorClient hierarchy."""
    insert_result = MagicMock()
    insert_result.inserted_ids = list(range(inserted_count))

    collection = MagicMock()
    collection.delete_many = AsyncMock(return_value=MagicMock())
    collection.insert_many = AsyncMock(return_value=insert_result)
    collection.create_index = AsyncMock(return_value="metadata.collection_1")

    db = MagicMock()
    db.marketplace_products = collection

    client = MagicMock()
    client.__getitem__ = MagicMock(return_value=db)
    client.close = MagicMock()
    return client, collection


# ---------------------------------------------------------------------------
# Catalogue structure tests (no I/O)
# ---------------------------------------------------------------------------

class TestMarketplaceProductsStructure(unittest.TestCase):
    def test_total_products_count(self) -> None:
        self.assertEqual(len(MARKETPLACE_PRODUCTS), 10)

    def test_five_distinct_collections(self) -> None:
        collections = {p["metadata"]["collection"] for p in MARKETPLACE_PRODUCTS}
        self.assertEqual(collections, {f"Master Look {i}" for i in range(1, 6)})

    def test_each_collection_has_two_products(self) -> None:
        for i in range(1, 6):
            count = sum(
                1 for p in MARKETPLACE_PRODUCTS
                if p["metadata"]["collection"] == f"Master Look {i}"
            )
            self.assertEqual(count, 2, msg=f"Master Look {i} must have exactly 2 products")

    def test_required_keys_present(self) -> None:
        required = {"name", "category", "brand", "price", "metadata"}
        for product in MARKETPLACE_PRODUCTS:
            self.assertEqual(required, required & product.keys(), msg=f"Missing keys in {product}")

    def test_elasticity_score_in_range(self) -> None:
        for product in MARKETPLACE_PRODUCTS:
            score = product["metadata"]["elasticity_score"]
            self.assertGreaterEqual(score, 0.0, msg=f"{product['name']} elasticity < 0")
            self.assertLessEqual(score, 1.0, msg=f"{product['name']} elasticity > 1")

    def test_prices_are_positive(self) -> None:
        for product in MARKETPLACE_PRODUCTS:
            self.assertGreater(product["price"], 0, msg=f"{product['name']} price <= 0")

    def test_each_collection_has_at_least_one_signature_piece(self) -> None:
        for i in range(1, 6):
            has_signature = any(
                p["metadata"].get("is_signature_piece")
                for p in MARKETPLACE_PRODUCTS
                if p["metadata"]["collection"] == f"Master Look {i}"
            )
            self.assertTrue(has_signature, msg=f"Master Look {i} has no signature piece")

    def test_master_look_1_contains_dior(self) -> None:
        look1 = [p for p in MARKETPLACE_PRODUCTS if p["metadata"]["collection"] == "Master Look 1"]
        brands = {p["brand"] for p in look1}
        self.assertIn("Dior", brands)

    def test_master_look_1_contains_prada(self) -> None:
        look1 = [p for p in MARKETPLACE_PRODUCTS if p["metadata"]["collection"] == "Master Look 1"]
        brands = {p["brand"] for p in look1}
        self.assertIn("Prada", brands)


# ---------------------------------------------------------------------------
# seed_products() async function — mocked MongoDB
# ---------------------------------------------------------------------------

class TestSeedProducts(unittest.TestCase):
    def _run_seed(self, mock_client, inserted_count=None):
        """Patch AsyncIOMotorClient and run seed_products()."""
        with patch("scripts.seed_marketplace_products.AsyncIOMotorClient", return_value=mock_client):
            _run(seed_products())

    def test_delete_many_called_once(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        collection.delete_many.assert_called_once_with({})

    def test_insert_many_called_once(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        collection.insert_many.assert_called_once()

    def test_insert_many_receives_all_products(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        args, _ = collection.insert_many.call_args
        self.assertEqual(args[0], MARKETPLACE_PRODUCTS)

    def test_create_index_called_on_metadata_collection(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        collection.create_index.assert_called_once_with([("metadata.collection", 1)])

    def test_client_close_always_called(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        client.close.assert_called_once()

    def test_client_close_called_even_on_exception(self) -> None:
        client, collection = _make_mock_client()
        collection.delete_many = AsyncMock(side_effect=RuntimeError("DB unavailable"))
        self._run_seed(client)
        client.close.assert_called_once()

    def test_insert_not_called_if_delete_raises(self) -> None:
        client, collection = _make_mock_client()
        collection.delete_many = AsyncMock(side_effect=RuntimeError("DB unavailable"))
        self._run_seed(client)
        collection.insert_many.assert_not_called()

    def test_correct_db_name_used(self) -> None:
        client, collection = _make_mock_client()
        self._run_seed(client)
        client.__getitem__.assert_called_with("dwelly_db")


# ---------------------------------------------------------------------------
# Environment / constants
# ---------------------------------------------------------------------------

class TestEnvironmentConstants(unittest.TestCase):
    def test_db_name_is_dwelly_db(self) -> None:
        self.assertEqual(seed_mod.DB_NAME, "dwelly_db")

    def test_default_mongodb_url(self) -> None:
        original = os.environ.pop("MONGODB_URL", None)
        try:
            importlib.reload(seed_mod)
            self.assertEqual(seed_mod.MONGODB_URL, "mongodb://localhost:27017")
        finally:
            if original is not None:
                os.environ["MONGODB_URL"] = original
            importlib.reload(seed_mod)

    def test_custom_mongodb_url_from_env(self) -> None:
        os.environ["MONGODB_URL"] = "mongodb://custom-host:27017"
        try:
            importlib.reload(seed_mod)
            self.assertEqual(seed_mod.MONGODB_URL, "mongodb://custom-host:27017")
        finally:
            os.environ.pop("MONGODB_URL", None)
            importlib.reload(seed_mod)


if __name__ == "__main__":
    unittest.main()

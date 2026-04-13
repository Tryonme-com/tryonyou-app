"""
Seed script for the Divineo marketplace_products collection.

Populates MongoDB with the 5 Master Looks used by TryOnYou's fit algorithm.
Each product includes an ``elasticity_score`` in ``metadata`` that drives
the Zero-Size garment-adjustment pipeline.

Usage:
    python scripts/seed_marketplace_products.py

Environment variables (via .env or shell):
    MONGODB_URL  — connection string (default: mongodb://localhost:27017)
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load credentials from .env; never hard-code secrets
load_dotenv()

MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME: str = "dwelly_db"

# ---------------------------------------------------------------------------
# 5 Master Looks — reference catalogue for the TryOnYou fit engine
# elasticity_score: 0 = rigid, 1 = fully elastic
# ---------------------------------------------------------------------------
MARKETPLACE_PRODUCTS: list[dict] = [
    # ── Master Look 1 ────────────────────────────────────────────────────────
    {
        "name": "Gabardina Dior Homme",
        "category": "Outerwear",
        "brand": "Dior",
        "price": 2800.00,
        "metadata": {
            "elasticity_score": 0.15,  # Rigid weave — precise fit
            "collection": "Master Look 1",
            "is_signature_piece": True,
        },
    },
    {
        "name": "Pantalón Sastre Prada",
        "category": "Trousers",
        "brand": "Prada",
        "price": 950.00,
        "metadata": {
            "elasticity_score": 0.45,  # Fluid drape — relaxed fit
            "collection": "Master Look 1",
        },
    },
    # ── Master Look 2 ────────────────────────────────────────────────────────
    {
        "name": "Blazer Balmain White Snap",
        "category": "Jacket",
        "brand": "Balmain",
        "price": 3200.00,
        "metadata": {
            "elasticity_score": 0.20,  # Structured — iconic Balmain shoulder
            "collection": "Master Look 2",
            "is_signature_piece": True,
        },
    },
    {
        "name": "Jean Skinny Balmain",
        "category": "Trousers",
        "brand": "Balmain",
        "price": 680.00,
        "metadata": {
            "elasticity_score": 0.55,  # Stretch denim — adaptive fit
            "collection": "Master Look 2",
        },
    },
    # ── Master Look 3 ────────────────────────────────────────────────────────
    {
        "name": "Vestido Valentino Couture",
        "category": "Dress",
        "brand": "Valentino",
        "price": 4500.00,
        "metadata": {
            "elasticity_score": 0.30,  # Silk blend — semi-rigid structure
            "collection": "Master Look 3",
            "is_signature_piece": True,
        },
    },
    {
        "name": "Cinturón Valentino Rockstud",
        "category": "Accessories",
        "brand": "Valentino",
        "price": 420.00,
        "metadata": {
            "elasticity_score": 0.05,  # Leather — no stretch
            "collection": "Master Look 3",
        },
    },
    # ── Master Look 4 ────────────────────────────────────────────────────────
    {
        "name": "Abrigo Elena Grandini Exclusive",
        "category": "Outerwear",
        "brand": "Elena Grandini",
        "price": 1850.00,
        "metadata": {
            "elasticity_score": 0.25,  # Woven wool — precise Zero-Size fit
            "collection": "Master Look 4",
            "is_signature_piece": True,
            "store_id": "EG-BOUTIQUE",
        },
    },
    {
        "name": "Falda Midi Elena Grandini",
        "category": "Skirts",
        "brand": "Elena Grandini",
        "price": 620.00,
        "metadata": {
            "elasticity_score": 0.40,  # Textured fabric — fluid movement
            "collection": "Master Look 4",
            "store_id": "EG-BOUTIQUE",
        },
    },
    # ── Master Look 5 ────────────────────────────────────────────────────────
    {
        "name": "Traje Sastre Lafayette Signature",
        "category": "Suit",
        "brand": "Galeries Lafayette Exclusive",
        "price": 1600.00,
        "metadata": {
            "elasticity_score": 0.18,  # Tailored canvas — sharp silhouette
            "collection": "Master Look 5",
            "is_signature_piece": True,
            "store_id": "GL-HAUSSMANN",
        },
    },
    {
        "name": "Camisa Algodón Lafayette Pilot",
        "category": "Shirts",
        "brand": "Galeries Lafayette Exclusive",
        "price": 280.00,
        "metadata": {
            "elasticity_score": 0.60,  # Soft cotton — relaxed biometric drape
            "collection": "Master Look 5",
            "store_id": "GL-HAUSSMANN",
        },
    },
]


async def seed_products() -> None:
    """Clean and reload marketplace products atomically."""
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    collection = db.marketplace_products

    try:
        print(f"📡 Conectando a {DB_NAME}...")

        # 1. Purge stale data
        await collection.delete_many({})
        print("🧹 Base de datos marketplace purgada.")

        # 2. Insert Master Looks catalogue
        if MARKETPLACE_PRODUCTS:
            result = await collection.insert_many(MARKETPLACE_PRODUCTS)
            print(f"✅ Se han cargado {len(result.inserted_ids)} productos maestros.")

        # 3. Create index for fast collection-based queries (target latency < 200 ms)
        await collection.create_index([("metadata.collection", 1)])
        print("🚀 Índices de búsqueda optimizados.")

    except Exception as exc:  # noqa: BLE001
        print(f"❌ Error durante el seeding: {exc}")
    finally:
        client.close()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(seed_products())

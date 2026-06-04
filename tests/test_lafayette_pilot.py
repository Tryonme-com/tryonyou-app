import os
import tempfile
import unittest

import api.index as api_index


class TestLafayettePilotEndpoints(unittest.TestCase):
    def setUp(self):
        self._tmp_db = tempfile.NamedTemporaryFile(delete=False)
        self._tmp_db.close()
        api_index.DB_PATH = self._tmp_db.name
        self.client = api_index.app.test_client()

    def tearDown(self):
        try:
            os.unlink(self._tmp_db.name)
        except FileNotFoundError:
            pass

    def test_cart_and_reservation_stock_lock(self):
        cart_res = self.client.post(
            "/api/lafayette/carrito",
            json={
                "session_id": "sess-A",
                "garment_id": "eg001",
                "look_name": "Robe Rouge Elena",
                "brand": "balmain",
                "fit_profile": "precision-couture",
            },
        )
        self.assertEqual(cart_res.status_code, 200)
        payload = cart_res.get_json()
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["cart_count"], 1)

        reserve_ok = self.client.post(
            "/api/lafayette/reservar",
            json={"session_id": "sess-A", "garment_id": "eg001", "brand": "balmain"},
        )
        self.assertEqual(reserve_ok.status_code, 200)
        reserve_payload = reserve_ok.get_json()
        self.assertEqual(reserve_payload["stock_lock"], "locked")
        self.assertTrue(reserve_payload["reserva_id"])

        reserve_conflict = self.client.post(
            "/api/lafayette/reservar",
            json={"session_id": "sess-B", "garment_id": "eg001", "brand": "balmain"},
        )
        self.assertEqual(reserve_conflict.status_code, 409)

    def test_collection_returns_five_with_four_alternatives(self):
        res = self.client.get("/api/lafayette/coleccion/balmain")
        self.assertEqual(res.status_code, 200)
        payload = res.get_json()
        self.assertEqual(len(payload["sugerencias_totales"]), 5)
        self.assertEqual(len(payload["alternativas"]), 4)

    def test_silhouette_store_and_share_privacy_rule(self):
        sil_res = self.client.post(
            "/api/lafayette/silueta/guardar",
            json={
                "session_id": "sess-silhouette",
                "biometric_snapshot": {
                    "lock_score": 0.92,
                    "shoulder_confidence": 0.93,
                },
            },
        )
        self.assertEqual(sil_res.status_code, 200)
        self.assertEqual(sil_res.get_json()["status"], "stored")

        share_bad = self.client.post(
            "/api/lafayette/look/compartir",
            json={
                "session_id": "sess-silhouette",
                "garment_id": "eg001",
                "brand": "balmain",
                "image_name": "bad.png",
                "metadata": {"weight": "62kg"},
            },
        )
        self.assertEqual(share_bad.status_code, 422)

        share_ok = self.client.post(
            "/api/lafayette/look/compartir",
            json={
                "session_id": "sess-silhouette",
                "garment_id": "eg001",
                "brand": "balmain",
                "image_name": "clean.png",
                "metadata": {"privacy_filter": "NO_WEIGHT_HEIGHT_DIMENSIONS_SIZE"},
            },
        )
        self.assertEqual(share_ok.status_code, 200)
        self.assertEqual(share_ok.get_json()["status"], "shared")


if __name__ == "__main__":
    unittest.main()

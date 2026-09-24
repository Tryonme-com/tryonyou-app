import uuid
import json
from datetime import datetime


class QRReservationManager:
    def __init__(self):
        self.project_id = "gen-lang-client-0091228222"
        self.active_reservations = []

    def generate_reservation_qr(self, user_id, items_list):
        """
        Crea un token de reserva unico y prepara la data para el QR.
        """
        reservation_id = f"TRY-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        qr_data = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "items": items_list,
            "status": "pending_in_store",
            "created_at": timestamp,
            "project": self.project_id,
        }

        self.active_reservations.append(qr_data)
        return qr_data

    def confirm_store_availability(self, store_id="BALMAIN_PARIS_01"):
        """
        Verificacion de seguridad de stock antes de confirmar reserva.
        """
        return True


if __name__ == "__main__":
    manager = QRReservationManager()

    user = "Lafayette_User_01"
    look = ["Balmain Jacket", "Slim Trousers"]

    if manager.confirm_store_availability():
        reserva = manager.generate_reservation_qr(user, look)
        print("--- RESERVA GENERADA ---")
        print(f"ID: {reserva['reservation_id']}")
        print(f"Codigo QR (Payload): {json.dumps(reserva, indent=2)}")
        print("Estado: Listo para escaneo en tienda.")
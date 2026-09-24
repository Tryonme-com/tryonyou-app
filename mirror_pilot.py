import uuid
import json

class DigitalMirrorPilot:
    def __init__(self):
        """Inicializa los contenedores de datos y contadores de métricas del piloto."""
        self.user_silhouette = None
        self.suggestions = []
        self.current_look_index = 0
        self.cart = []
        self.metrics = {
            "clicks_perfect_selection": 0,
            "clicks_reserve_fitting_room": 0,
            "clicks_view_combinations": 0,
            "clicks_save_silhouette": 0,
            "clicks_share_look": 0,
            "snap_triggers": 0
        }

    def process_scan(self, measurements: dict):
        self.user_silhouette = {
            "user_id": str(uuid.uuid4()),
            "measurements": measurements,
            "perfect_size": self._calculate_exact_size(measurements)
        }
        return self.user_silhouette

    def _calculate_exact_size(self, measurements: dict) -> str:
        bust = measurements.get("bust", 0)
        if bust > 95:
            return "Size_B"
        return "Size_A"

    def load_suggestions(self, items_pool: list):
        self.suggestions = items_pool[:5]
        self.current_look_index = 0

    def trigger_snap(self):
        self.metrics["snap_triggers"] += 1
        return {"event": "snap_detected", "action": "switch_to_full_look"}

    def action_perfect_selection(self):
        self.metrics["clicks_perfect_selection"] += 1
        if not self.suggestions or not self.user_silhouette:
            return {"status": "error", "message": "Missing scan or suggestions"}
        selected_look = self.suggestions[self.current_look_index]
        self.cart.append({
            "look": selected_look,
            "size": self.user_silhouette["perfect_size"]
        })
        return {"status": "success", "added_to_cart": selected_look}

    def action_reserve_fitting_room(self):
        self.metrics["clicks_reserve_fitting_room"] += 1
        if not self.user_silhouette:
            return {"status": "error", "message": "Missing scan data"}
        
        reservation_id = str(uuid.uuid4())
        qr_payload = {
            "reservation_id": reservation_id,
            "size": self.user_silhouette["perfect_size"]
        }
        return {"status": "reserved", "qr_code_data": json.dumps(qr_payload)}

    def action_view_combinations(self):
        self.metrics["clicks_view_combinations"] += 1
        if len(self.suggestions) > 0:
            self.current_look_index = (self.current_look_index + 1) % len(self.suggestions)
        return {"current_index": self.current_look_index, "look": self.suggestions[self.current_look_index]}

    def action_save_silhouette(self):
        self.metrics["clicks_save_silhouette"] += 1
        if self.user_silhouette:
            return {"status": "saved", "profile_id": self.user_silhouette["user_id"]}
        return {"status": "error", "message": "No scan data to save"}

    def action_share_look(self):
        self.metrics["clicks_share_look"] += 1
        if not self.suggestions:
            return {"status": "error", "message": "No look selected"}
        return {
            "status": "ready_to_share",
            "image_layer": self.suggestions[self.current_look_index],
            "hidden_fields": ["weight", "height", "size", "measurements"]
        }

    def get_metrics(self) -> dict:
        """Returns collected validation metrics."""
        return self.metrics

if __name__ == "__main__":
    mirror = DigitalMirrorPilot()
    mock_measurements = {"bust": 98, "waist": 78, "hips": 102}
    mirror.process_scan(mock_measurements)
    mock_items = ["Item_Alpha", "Item_Beta", "Item_Gamma", "Item_Delta", "Item_Epsilon"]
    mirror.load_suggestions(mock_items)
    
    mirror.trigger_snap()
    mirror.action_perfect_selection()
    mirror.action_reserve_fitting_room()
    mirror.action_view_combinations()
    mirror.action_share_look()
    
    print(json.dumps(mirror.get_metrics(), indent=4))

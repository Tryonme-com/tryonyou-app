import json
import os
from datetime import datetime

class TryOnYouAnalytics:
    def __init__(self):
        self.log_file = "pilot_analytics.json"
        self.patent = "PCT/EP2025/067317"

    def log_interaction(self, action_type="SNAP_ACTIVATE", brand="Balmain"):
        print(f"--- 📊 REGISTRANDO MÉTRICA DE TRACCIÓN ---")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "action": action_type,
            "brand": brand,
            "verification_status": "PATENT_PROTECTED",
            "patent_ref": self.patent
        }

        # Leer logs existentes o crear nuevos
        logs = []
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                logs = json.load(f)
        
        logs.append(entry)
        
        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=4)
        
        print(f"✅ Interacción {action_type} guardada. Total métricas: {len(logs)}")

if __name__ == "__main__":
    analytics = TryOnYouAnalytics()
    analytics.log_interaction("VIP_RESERVATION_COMPLETE")

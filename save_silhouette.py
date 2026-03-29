import json
import hashlib

def save_secure_silhouette(user_measurements):
    # Encriptamos para que nadie vea datos sensibles (peso/altura)
    # Solo guardamos un "Fit-ID" único
    raw_data = json.dumps(user_measurements).encode()
    fit_id = hashlib.sha256(raw_data).hexdigest()[:12]
    
    profile = {
        "fit_id": fit_id,
        "algorithm": "v10_ultimate",
        "last_scan": "2026-03-29",
        "client_id": "gen-lang-client-0091228222"
    }
    
    print(f"\n[👤 SILUETA] Escaneo procesado con éxito.")
    print(f"[🔐 SEGURIDAD] Datos biométricos convertidos a Fit-ID: {fit_id}")
    
    with open('user_silhouette.json', 'w') as f:
        json.dump(profile, f, indent=4)
        
    return "✅ Silueta guardada: Experiencia sin complejos activada."

if __name__ == "__main__":
    # Simulación de datos de escaneo (estos no se guardan tal cual)
    measurements = {"height": 180, "chest": 100, "waist": 85}
    print(save_secure_silhouette(measurements))

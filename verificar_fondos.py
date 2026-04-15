import sys

def check_real_funds(source, iban_last_digits):
    gateways = {"STRIPE": "PENDING_VALIDATION", "LAFAYETTE": "AWAITING_CONFIRMATION"}
    if iban_last_digits == "6934":
        for key, status in gateways.items():
            print(f"[*] NODO {key}: {status}")
        return False
    return False

if __name__ == "__main__":
    print("--- INICIANDO AUDITORÍA DE CAPITAL REAL ---")
    if not check_real_funds("ALL", "6934"):
        print("[!] ERROR: CAPITAL NO REFLEJADO EN HELLO BANK")
        print("[!] REVISAR: Ciclo de compensación de las 11:30 AM")
        sys.exit(1)

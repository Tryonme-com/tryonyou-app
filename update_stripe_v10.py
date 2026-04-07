import stripe

# SUSTITUYE POR TU LLAVE NUEVA SIN TOCAR NADA MÁS
stripe.api_key = "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"

def crear_productos_v10():
    print("🚀 Iniciando inyección Soberanía V10 con llave verificada...")
    productos = [
        {"name": "V10-LAFAYETTE-ENTRY-P1", "amount": 2750000, "desc": "Activacion V10: Setup 10 Nodos + Exclusividad D9."},
        {"name": "V10-ENTRY-GLOBAL", "amount": 2500000, "desc": "Despliegue V10: Instalacion 10 Nodos (LVMH/Otros)."},
        {"name": "IP-TRANSFER-V10-P1", "amount": 9825000, "desc": "Transferencia de Activos/Licencia IP (Parte 1)."},
        {"name": "IP-TRANSFER-V10-P2", "amount": 9825000, "desc": "Transferencia de Activos/Licencia IP (Parte 2)."},
        {"name": "V10-ANUAL-PREPAGO", "amount": 9800000, "desc": "Abono Anual 10 nodos (Ahorro 20k) + 8% Comision sobre ventas."},
    ]

    for p in productos:
        try:
            prod = stripe.Product.create(name=p["name"], description=p["desc"])
            stripe.Price.create(unit_amount=p["amount"], currency="eur", product=prod.id)
            print(f"✅ Creado: {p['name']}")
        except Exception as e:
            print(f"❌ Error en {p['name']}: {str(e)}")

    try:
        mensual = stripe.Product.create(name="V10-MANTENIMIENTO-MENSUAL", description="Canon mensual 10 nodos + 8% Comision.")
        stripe.Price.create(unit_amount=990000, currency="eur", recurring={"interval": "month"}, product=mensual.id)
        print("✅ Suscripción Mensual Creada: 9.900€")
    except Exception as e:
        print(f"❌ Error en Suscripción: {str(e)}")

if __name__ == "__main__":
    crear_productos_v10()

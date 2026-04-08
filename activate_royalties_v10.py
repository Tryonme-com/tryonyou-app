import stripe

from sovereign_script_env import require_stripe_secret


def activar_8_por_ciento():
    stripe.api_key = require_stripe_secret()
    print("🛰️ Configurando Meter (Protocolo Basil) y Royalty 8%...")
    try:
        # 1. Crear el Meter con el mapeo de tipo obligatorio
        meter = stripe.billing.Meter.create(
            display_name="Ventas Totales Escaparate V10",
            event_name="v10_sale_event",
            default_aggregation={"formula": "sum"},
            customer_mapping={
                "type": "by_id",  # Stripe: cliente identificado por ID en el payload del evento
                "event_payload_key": "stripe_customer_id",
            },
        )
        print(f"✅ Meter creado con éxito: {meter.id}")

        # 2. Crear el producto de Royalty
        royalty_v10 = stripe.Product.create(
            name="V10-ROYALTY-VENTA-TOTAL",
            description="Comision del 8% sobre la facturacion bruta total detectada por el contador V10."
        )

        # 3. Vincular el precio al Meter (8 céntimos por cada 1€)
        precio_comision = stripe.Price.create(
            currency="eur",
            product=royalty_v10.id,
            billing_scheme="per_unit",
            unit_amount_decimal="8.0", 
            recurring={
                "interval": "month",
                "usage_type": "metered",
                "meter": meter.id
            }
        )

        print(f"✅ SISTEMA DE COMISION DEL 8% SELLADO Y OPERATIVO.")
        print(f"ID del Royalty: {precio_comision.id}")
        
    except Exception as e:
        print(f"❌ Error en Protocolo Basil: {str(e)}")

if __name__ == "__main__":
    activar_8_por_ciento()

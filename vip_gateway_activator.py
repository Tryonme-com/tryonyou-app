import os

def activate_commerce():
    print("--- 💳 ACTIVANDO MOTOR COMERCIAL V10 ---")
    html_path = "index.html"
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        
        # Inyectar el script de checkout seguro antes del cierre del body
        checkout_script = """
        <script>
            function processSovereignPayment(amount) {
                console.log("Iniciando cobro seguro para Rubén Espinar...");
                window.location.href = "https://checkout.tryonyou.app/pay?founder=ruben&siret=94361019600017";
            }
        </script>
        """
        if "processSovereignPayment" not in content:
            new_content = content.replace("</body>", f"{checkout_script}</body>")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Pasarela de pago VIP inyectada en el Espejo.")
        else:
            print("⚠️ La pasarela ya estaba activa.")

if __name__ == "__main__":
    activate_commerce()

import os

def inject_share_system():
    print("--- 📸 ACTIVANDO MOTOR DE SILUETAS COMPARTIBLES ---")
    html_path = "index.html"
    
    share_ui = """
    <div id="share-container" style="position: absolute; bottom: 150px; right: 20px; z-index: 1005;">
        <button onclick="captureSilhouette()" style="background: rgba(212, 175, 55, 0.9); color: #000; border: none; padding: 12px 20px; font-weight: bold; cursor: pointer; font-family: sans-serif; border-radius: 5px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
            PARTAGER MON LOOK VIP
        </button>
    </div>

    <script>
        function captureSilhouette() {
            console.log("Generando imagen de silueta con patente PCT/EP2025/067317...");
            // Lógica para exportar el canvas del Robert Engine
            const canvas = document.getElementById('output_canvas');
            if (canvas) {
                const dataURL = canvas.toDataURL("image/png");
                alert("Votre silhouette Balmain V10 est prête. Le lien de partage sécurisé a été envoyé a RUBENSANZBUROBOT.");
                
                // Enviar señal al bot del Fundador
                fetch('/api/signal-share', { 
                    method: 'POST', 
                    body: JSON.stringify({ action: "USER_SHARE_LOOK", brand: "BALMAIN" }) 
                });
            }
        }
    </script>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        if "captureSilhouette" not in content:
            new_content = content.replace("</body>", f"{share_ui}</body>")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Motor de Siluetas Compartibles inyectado.")

if __name__ == "__main__":
    inject_share_system()

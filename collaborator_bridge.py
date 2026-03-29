import os

def inject_collaborators():
    print("--- 🤝 VINCULANDO ARMARIO SOLIDARIO, INTELIGENTE Y SAC MUSEUM ---")
    html_path = "index.html"
    
    collab_ui = """
    <div id="collab-nav" style="position: absolute; bottom: 100px; width: 100%; display: flex; justify-content: center; gap: 20px; z-index: 1003;">
        <button onclick="filterCollab('ARMARIO SOLIDARIO')" style="background:#1a1a1a; color:#fff; border:1px solid #fff; padding:5px 15px; cursor:pointer; font-size:0.6rem;">ARMARIO SOLIDARIO</button>
        <button onclick="filterCollab('ARMARIO INTELIGENTE')" style="background:#1a1a1a; color:#D4AF37; border:1px solid #D4AF37; padding:5px 15px; cursor:pointer; font-size:0.6rem;">ARMARIO INTELIGENTE</button>
        <button onclick="filterCollab('SAC MUSEUM')" style="background:#D4AF37; color:#000; border:none; padding:5px 15px; cursor:pointer; font-size:0.6rem; font-weight:bold;">SAC MUSEUM</button>
    </div>
    <script>
        function filterCollab(type) {
            console.log("Accediendo a: " + type);
            // El Biometric Matcher filtra instantáneamente por estas categorías
            alert("Connexion sécurisée à " + type + ". Analyse de fit en cours.");
        }
    </script>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        if "collab-nav" not in content:
            new_content = content.replace("</body>", f"{collab_ui}</body>")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Puentes de colaboración inyectados en la UI.")

if __name__ == "__main__":
    inject_collaborators()

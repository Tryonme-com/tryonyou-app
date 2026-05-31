import os

def secure_domains():
    print("--- 🌐 ORQUESTANDO SOBERANÍA DE DOMINIOS ---")
    html_path = "index.html"
    
    # Script para validar que el usuario está en el búnker correcto
    shield_script = """
    <script>
        const authorizedDomains = ['tryonme.app', 'localhost'];
        const currentHost = window.location.hostname;
        
        if (!authorizedDomains.some(domain => currentHost.includes(domain))) {
            console.log("⚠️ Acceso vía Satélite detectado. Validando integridad...");
        }
        
        function showSovereignInfo() {
            alert("Réseau TryOnMe : abvetos.com | tryonme.com | tryonme.org - Piloté par Rubén Espinar.");
        }
    </script>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        if "authorizedDomains" not in content:
            new_content = content.replace("</body>", f"{shield_script}</body>")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Escudo de Red de Dominios inyectado.")

if __name__ == "__main__":
    secure_domains()

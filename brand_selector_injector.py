import os

def inject_brands():
    print("--- 🏷️ ACTIVANDO MULTI-MARCA: NIVEL GALERIES LAFAYETTE ---")
    html_path = "index.html"
    
    brand_ui = """
    <div id="brand-nav" style="position: absolute; top: 100px; width: 100%; display: flex; justify-content: center; gap: 30px; z-index: 1002; background: rgba(0,0,0,0.5); padding: 10px 0;">
        <span onclick="filterBrand('BALMAIN')" style="color:#D4AF37; cursor:pointer; font-size:0.8rem; letter-spacing:2px;">BALMAIN</span>
        <span onclick="filterBrand('CHANEL')" style="color:#fff; cursor:pointer; font-size:0.8rem; letter-spacing:2px;">CHANEL</span>
        <span onclick="filterBrand('DIOR')" style="color:#fff; cursor:pointer; font-size:0.8rem; letter-spacing:2px;">DIOR</span>
        <span onclick="filterBrand('SAINT LAURENT')" style="color:#fff; cursor:pointer; font-size:0.8rem; letter-spacing:2px;">YSL</span>
        <span onclick="filterBrand('JACQUEMUS')" style="color:#fff; cursor:pointer; font-size:0.8rem; letter-spacing:2px;">JACQUEMUS</span>
    </div>
    <script>
        function filterBrand(brandName) {
            console.log("Filtrando catálogo por: " + brandName);
            // Aquí Robert Engine filtra las 5 mejores prendas de esa marca específica
            alert("Accès au catalogue " + brandName + " optimisé pour votre silhouette.");
        }
    </script>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        if "brand-nav" not in content:
            new_content = content.replace("<body>", f"<body>{brand_ui}")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Navegación multi-marca inyectada.")

if __name__ == "__main__":
    inject_brands()

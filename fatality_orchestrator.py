import os

def activate_fatality():
    print("--- 🎭 ACTIVANDO EL EFECTO PALOMA: DOSSIER FATALITY ---")
    html_path = "index.html"
    
    # Inyectamos el pie de página de alianzas y el acceso al Dossier
    fatality_footer = """
    <div id="fatality-partners" style="position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: space-around; opacity: 0.4; filter: grayscale(1); transition: 0.5s; z-index: 1004;">
        <img src="assets/liveitfashion_logo.png" style="height: 25px;">
        <img src="assets/vvlart_logo.png" style="height: 25px;">
        <span style="font-family:serif; color:#fff; font-size:0.7rem; letter-spacing:3px;">LA MESA DE LOS LISTOS</span>
    </div>
    <script>
        // Si el Fit Score es > 98%, el Efecto Paloma se activa
        function applyPalomaEffect() {
            console.log("Efecto Paloma: Elegancia absoluta detectada.");
            document.body.style.boxShadow = "inset 0 0 100px rgba(212, 175, 55, 0.2)";
            alert("L'EFFET PALOMA : Silhouette validée par le protocole Fatality.");
        }
    </script>
    <style>
        #fatality-partners:hover { opacity: 1; filter: grayscale(0); }
    </style>
    """
    
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            content = f.read()
        if "fatality-partners" not in content:
            new_content = content.replace("</footer>", f"{fatality_footer}</footer>")
            with open(html_path, "w") as f:
                f.write(new_content)
            print("✅ Efecto Paloma e iconos estratégicos integrados.")

if __name__ == "__main__":
    activate_fatality()

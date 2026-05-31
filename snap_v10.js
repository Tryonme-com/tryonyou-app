function activateSnap() {
    const mirror = document.getElementById('tryon-mirror-container');
    const overlay = document.getElementById('overlay-garment');
    
    // Efecto de brillo intenso (Chasquido)
    mirror.style.transition = "filter 0.1s ease-in-out";
    mirror.style.filter = "brightness(3) contrast(1.2) grayscale(0)";
    
    setTimeout(() => {
        // Inyectar la prenda Balmain
        overlay.style.display = 'block';
        overlay.style.opacity = '1';
        
        // Volver al estilo elegante
        mirror.style.filter = "grayscale(0.5)";
        console.log("⚡ SNAP V10: Look Balmain aplicado bajo Patente PCT/EP2025/067317.");
        
        // Registrar métrica en el servidor
        fetch('/log-snap', { method: 'POST' });
    }, 150);
}

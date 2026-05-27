document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');
    const scanLine = document.getElementById('scan-line');
    const svg = document.getElementById('biometric-svg');
    const biometricForm = document.getElementById('biometric-form');
    const btnPerfectSelection = document.getElementById('btn-perfect-selection');

    // 1. Inicializar Cámara vía WebRTC
    async function initCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });
            video.srcObject = stream;
        } catch (err) {
            console.error("Error al acceder a la cámara: ", err);
            alert("Por favor, permite el acceso a la cámara para usar el espejo digital.");
        }
    }

    // 2. Animar línea del escáner
    let pos = 0;
    let direction = 1;
    function animateScanner() {
        pos += direction * 2;
        if (pos > 600 || pos < 0) direction *= -1;
        scanLine.setAttribute('y1', pos);
        scanLine.setAttribute('y2', pos);
        requestAnimationFrame(animateScanner);
    }

    // 3. Generar Puntos Biométricos Visuales
    function createBiometricPoints() {
        const pointsCount = 12;
        for (let i = 0; i < pointsCount; i++) {
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute('class', 'biometric-point');
            circle.setAttribute('r', '3');
            const x = Math.random() * 400;
            const y = Math.random() * 600;
            circle.setAttribute('cx', x);
            circle.setAttribute('cy', y);
            circle.style.animation = `pulse ${1 + Math.random() * 2}s infinite`;
            circle.style.opacity = Math.random();
            svg.appendChild(circle);
        }
    }

    // 4. Conexión Real con la API (Mi Selección Perfecta)
    if (btnPerfectSelection) {
        btnPerfectSelection.addEventListener('click', async (e) => {
            e.preventDefault();

            // Validar que el usuario haya rellenado altura y peso
            if (!biometricForm.checkValidity()) {
                biometricForm.reportValidity();
                return;
            }

            // Efecto visual de pulsación
            btnPerfectSelection.style.transform = 'scale(0.95)';
            setTimeout(() => btnPerfectSelection.style.transform = 'scale(1)', 100);

            // Recoger datos reales introducidos por el usuario
            const payload = {
                height: parseFloat(document.getElementById('height').value),
                weight: parseFloat(document.getElementById('weight').value),
                event_type: document.getElementById('event').value
            };

            try {
                // Llamada al backend de producción
                const response = await fetch('https://tryonyou.app/api/recommendation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) throw new Error(`Error en servidor: ${response.status}`);

                const data = await response.json();

                // FLUJO CORRECTO: si el backend devuelve la prenda ideal, se inicializa el Checkout/PaymentIntent
                if (data.checkoutUrl) {
                    // Redirección al flujo de pago seguro que posteriormente activará el Webhook de Stripe
                    window.location.href = data.checkoutUrl;
                } else {
                    console.warn('La respuesta de la API no incluyó checkoutUrl:', data);
                }

            } catch (error) {
                console.error("Fallo en la comunicación con el motor TryOnYou:", error);
            }
        });
    }

    // Resto de botones (Efecto visual básico)
    const otherButtons = document.querySelectorAll('.btn-luxury:not(#btn-perfect-selection)');
    otherButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => btn.style.transform = 'scale(1)', 100);
            console.log(`Acción activada: ${e.target.innerText}`);
        });
    });

    // Inicializar componentes
    initCamera();
    animateScanner();
    createBiometricPoints();
});

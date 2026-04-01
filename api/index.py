<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TRYONME - SOUVERAINETÉ V10</title>
    
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>
    
    <style>
        :root { --gold: #D4AF37; --black: #000; --glass: rgba(0,0,0,0.7); }
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }
        body { background: var(--black); color: white; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; overflow: hidden; height: 100vh; }

        /* CAPA 0: EL ESPEJO (EL MOTOR) */
        #mirror-container {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1;
        }
        video#webcam { position: absolute; opacity: 0; width: 1px; height: 1px; }
        canvas#output_canvas { width: 100%; height: 100%; object-fit: cover; }

        /* CAPA 1: HEADER SOBERANO */
        header {
            position: fixed; top: 0; width: 100%; z-index: 100;
            padding: 40px 20px; text-align: center;
            background: linear-gradient(to bottom, rgba(0,0,0,0.9), transparent);
        }
        .logo { font-size: 1.4rem; letter-spacing: 12px; font-weight: 200; text-transform: uppercase; margin-bottom: 15px; }
        .brand-nav { display: flex; justify-content: center; gap: 25px; font-size: 0.65rem; letter-spacing: 4px; color: #666; }
        .brand-nav span:hover { color: var(--gold); cursor: pointer; }

        /* CAPA 2: HERO TEXT (CENTRO LIMPIO) */
        .hero-ui {
            position: absolute; width: 100%; top: 30%; text-align: center; z-index: 10; pointer-events: none;
        }
        .hero-ui h1 { font-size: 2.2rem; letter-spacing: 15px; font-weight: 100; text-transform: uppercase; }
        .hero-ui .highlight { color: var(--gold); font-weight: 400; }
        .date { font-size: 0.8rem; letter-spacing: 6px; margin-top: 25px; color: var(--gold); }

        /* CAPA 3: UI DE ACCIÓN (SISTEMA DE ARMARIOS) */
        .ui-controls {
            position: fixed; bottom: 0; width: 100%; z-index: 100;
            background: var(--glass); backdrop-filter: blur(20px);
            border-top: 0.5px solid rgba(255,255,255,0.1);
        }
        .cabinet-grid {
            display: grid; grid-template-columns: repeat(3, 1fr);
        }
        .btn-cabinet {
            background: transparent; border: 0.5px solid rgba(255,255,255,0.05);
            color: white; padding: 25px 10px; font-size: 0.6rem; letter-spacing: 3px;
            cursor: pointer; text-transform: uppercase; transition: 0.4s;
        }
        .btn-cabinet:hover { background: white; color: black; }
        .btn-pay {
            width: 100%; background: var(--gold); color: black; font-weight: 700;
            padding: 30px; font-size: 0.9rem; border: none; cursor: pointer;
            text-transform: uppercase; letter-spacing: 5px;
        }

        /* CAPA 4: FOOTER LEGAL */
        footer {
            position: fixed; bottom: 130px; width: 100%; text-align: center;
            font-size: 0.45rem; color: #444; letter-spacing: 2px; z-index: 90;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo">TRYONME</div>
        <div class="brand-nav">
            <span>BALMAIN</span><span>CHANEL</span><span>DIOR</span><span>YSL</span>
        </div>
    </header>

    <div class="hero-ui">
        <h1>ARRÊTEZ LE <span class="highlight">FAUX-FIT</span></h1>
        <div class="date">MAI 2026</div>
    </div>

    <div id="mirror-container">
        <video id="webcam" autoplay playsinline muted></video>
        <canvas id="output_canvas"></canvas>
    </div>

    <footer>SIRET: 94361019600017 | PATENTE: PCT/EP2025/067317</footer>

    <div class="ui-controls">
        <div class="cabinet-grid">
            <button class="btn-cabinet" onclick="alert('Armoire Solidaire Actif')">Solidaire</button>
            <button class="btn-cabinet" onclick="alert('Armoire Intelligent Actif')">Intelligent</button>
            <button class="btn-cabinet" onclick="alert('SAC Museum Actif')">Museum</button>
        </div>
        <button class="btn-pay" onclick="window.location.href='https://buy.stripe.com/test_soberania_4_5'">
            SOUVERAINETÉ : PAYER 12.500 €
        </button>
    </div>

    <script>
        const videoElement = document.getElementById('webcam');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d');

        function onResults(results) {
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.restore();
        }

        const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
        pose.setOptions({ modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5 });
        pose.onResults(onResults);

        const camera = new Camera(videoElement, {
            onFrame: async () => { await pose.send({image: videoElement}); },
            width: 1280, height: 720
        });
        camera.start();

        function resize() {
            canvasElement.width = window.innerWidth;
            canvasElement.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();
    </script>
</body>
</html>
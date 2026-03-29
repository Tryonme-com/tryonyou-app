/**
 * ROBERT ENGINE - EDITORIAL & BIOMETRIC SYNC V10
 * Patent: PCT/EP2025/067317 | Founder: Ruben Espinar Rodriguez
 * Focus: High-End Styling (Smokey Eyes, Wet Look, Waves)
 */

// MediaPipe Face Mesh landmark indices
const LANDMARK_LEFT_EYE_IRIS = [468, 469, 470, 471, 472];
const LANDMARK_RIGHT_EYE_IRIS = [473, 474, 475, 476, 477];
const LANDMARK_JAW_LEFT = 234;
const LANDMARK_JAW_RIGHT = 454;
const LANDMARK_CHIN = 152;
const LANDMARK_FOREHEAD = 10;
const GENDER_JAW_WIDTH_RATIO_THRESHOLD = 0.75;

const StylingConfig = {
    makeup: {
        smokeyIntensity: 0.6,
        color: [20, 20, 20], // Carbón Editorial
        blur: 12
    },
    hair: {
        gloss: 1.5, // Brillo Gomina
        waves: "Greek_Style", // Ondas al agua
        slickBack: "Gentleman_Style" // Gomina atrás
    }
};

class EditorialEngine {
    constructor(canvasCtx) {
        this.ctx = canvasCtx;
    }

    // 1. MAQUILLAJE AHUMADO (Smokey Eyes)
    applySmokeyEyes(landmarks) {
        const leftEye = LANDMARK_LEFT_EYE_IRIS;
        const rightEye = LANDMARK_RIGHT_EYE_IRIS;

        this.ctx.save();
        this.ctx.filter = `blur(${StylingConfig.makeup.blur}px)`;
        this.ctx.fillStyle = `rgba(${StylingConfig.makeup.color.join(',')}, ${StylingConfig.makeup.smokeyIntensity})`;

        this.drawPath(landmarks, leftEye);
        this.drawPath(landmarks, rightEye);

        this.ctx.restore();
    }

    // 2. EFECTO GOMINA / WET LOOK (Hair Gloss Shader)
    applyHairStyling(segmentationMask, gender) {
        this.ctx.save();

        // Dibujar la máscara de segmentación como base
        this.ctx.drawImage(segmentationMask, 0, 0);

        // Aplicar el brillo de la gomina usando un gradiente radial sobre la máscara
        this.ctx.globalCompositeOperation = 'soft-light';
        const gradient = this.ctx.createRadialGradient(
            this.ctx.canvas.width / 2, 100, 50,
            this.ctx.canvas.width / 2, 100, 300
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0.4)'); // Reflejo foco
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);

        this.ctx.restore();
        console.log(`✨ Estilismo aplicado: ${gender === 'male' ? 'Slick Back' : 'Ondas al Agua'}`);
    }

    drawPath(landmarks, indices) {
        this.ctx.beginPath();
        indices.forEach((idx, i) => {
            const point = landmarks[idx];
            if (i === 0) this.ctx.moveTo(point.x * this.ctx.canvas.width, point.y * this.ctx.canvas.height);
            else this.ctx.lineTo(point.x * this.ctx.canvas.width, point.y * this.ctx.canvas.height);
        });
        this.ctx.closePath();
        this.ctx.fill();
    }
}

/**
 * Detects gender based on facial landmark geometry.
 * Returns 'male' or 'female' as a best-effort estimate.
 * @param {Array} faceLandmarks - MediaPipe face landmarks array
 * @returns {'male'|'female'}
 */
function detectGender(faceLandmarks) {
    if (!faceLandmarks || faceLandmarks.length === 0) return 'female';
    // Placeholder heuristic: jaw width vs face height ratio
    const jaw = faceLandmarks[LANDMARK_JAW_LEFT];
    const jawRight = faceLandmarks[LANDMARK_JAW_RIGHT];
    const chin = faceLandmarks[LANDMARK_CHIN];
    const forehead = faceLandmarks[LANDMARK_FOREHEAD];
    if (!jaw || !jawRight || !chin || !forehead) return 'female';
    const jawWidth = Math.abs(jawRight.x - jaw.x);
    const faceHeight = Math.abs(chin.y - forehead.y);
    return jawWidth / faceHeight > GENDER_JAW_WIDTH_RATIO_THRESHOLD ? 'male' : 'female';
}

// Orquestador de Agentes EPT
export const runEditorialSuite = (results, canvasCtx) => {
    const engine = new EditorialEngine(canvasCtx);
    const gender = results.faceLandmarks ? detectGender(results.faceLandmarks) : 'female';

    if (results.faceLandmarks) engine.applySmokeyEyes(results.faceLandmarks);
    if (results.segmentationMask) engine.applyHairStyling(results.segmentationMask, gender);
};

export { EditorialEngine, StylingConfig, detectGender };

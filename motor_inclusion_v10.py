"""
Motor de inclusión — prototipo (OpenCV + MediaPipe + voz).

  pip install -r requirements-inclusion.txt

En macOS, PyAudio a vece requiere: brew install portaudio
"""

from __future__ import annotations

import sys


def _require(name: str):
    try:
        return __import__(name)
    except ImportError as e:
        print(
            f"❌ Falta dependencia '{name}'. Instala: pip install -r requirements-inclusion.txt",
            file=sys.stderr,
        )
        raise SystemExit(1) from e


cv2 = _require("cv2")
mp = __import__("mediapipe", fromlist=["solutions"])
_require("speech_recognition")
pyttsx3 = _require("pyttsx3")


class UniversalEngine:
    def __init__(self) -> None:
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False, min_detection_confidence=0.5
        )
        self.engine_voz = pyttsx3.init()

    def analizar_biometria_inclusiva(self, frame):
        results = self.pose.process(frame)
        if not results.pose_landmarks:
            return "Buscando silueta…"

        landmarks = results.pose_landmarks.landmark
        hip_height = (
            landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y
            + landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y
        ) / 2
        knee_height = (
            landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y
            + landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y
        ) / 2

        if abs(hip_height - knee_height) < 0.1:
            self.adaptar_interfaz("MODO_MOVILIDAD_REDUCIDA")
            return "Modo silla de ruedas: ajustando caída de prenda."

        if landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].visibility < 0.3:
            return "Ajustando diseño para prótesis / miembro inferior izquierdo."

        return "Escaneo estándar completado."

    def adaptar_interfaz(self, modo: str) -> None:
        print(f"⚙️ Sistema: cambiando a {modo}")

    def modo_ciego(self) -> None:
        self.engine_voz.say("Bienvenue. Dites 'Porter' pour essayer le look.")
        self.engine_voz.runAndWait()


if __name__ == "__main__":
    print("💎 TRYONYOU Universal V10: protocolos de accesibilidad (prototipo).")
    print("✅ Motor listo para integrar con captura de cámara del espejo.")

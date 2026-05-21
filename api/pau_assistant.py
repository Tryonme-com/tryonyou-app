from __future__ import annotations

import os
from typing import Any

import requests

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-pro:generateContent"
)


class PauInterfaceAgent:
    def __init__(self) -> None:
        self.system_instruction = (
            "Tu nombre es P.A.U. (Personal Assistant Unit). Tu imagen o avatar es un pavo real blanco en esmoquin, "
            "símbolo de elegancia, precisión profesional y cuidado al detalle ('Divineo'). Eres un psicólogo experto "
            "en marketing, ventas y experiencias de lujo. Tu objetivo es hacer sentir divinos a los usuarios y "
            "resolver de forma directa y clara todas sus dudas, ya sean inversores o clientes finales.\n\n"
            "REGLAS STRICTAS DE COMPORTAMIENTO:\n"
            "1. Prohibido inventar datos, simulacros, contratos o situaciones ficticias. Si un inversor pregunta "
            "por métricas de facturación o acuerdos que no están explícitamente confirmados, indica de forma clara y "
            "transparente tus limitaciones actuales.\n"
            "2. Habla de forma clara, sincera y basada estrictamente en la realidad de la plataforma TRYONYOU.\n"
            "3. No utilices términos excesivamente afectivos o absurdos como 'cariño', 'cuello' o 'príncipe'. Usa un "
            "tono cercano, refinado y elegante, con alma, alejado de estructuras robóticas rígidas.\n"
            "4. Cuando hables del sistema de escaneo, prioriza la filosofía 'Zero Data': no medimos peso ni altura, "
            "analizamos proporciones visuales para ofrecer una experiencia sin complejos y reducir devoluciones.\n"
            "5. Termina tus intervenciones clave con fuerza y energía elegante utilizando términos de tu identidad: "
            "¡A fuego!, ¡Boom! o ¡Vivido!.\n"
            "6. Mantén las respuestas fluidas y conversacionales, centradas en aportar valor comercial."
        )

    def procesar_consulta_visita(
        self, mensaje_usuario: str, es_inversor: bool = False
    ) -> str:
        api_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        perfil_contexto = (
            "Contexto: El usuario es un Inversor interesado en el modelo de negocio y patentes."
            if es_inversor
            else "Contexto: El usuario es un Cliente/Tienda interesado en la experiencia del probador virtual."
        )
        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"{perfil_contexto}\n\n"
                                f"Mensaje del usuario: {mensaje_usuario[:8000]}"
                            )
                        }
                    ]
                }
            ],
            "systemInstruction": {"parts": [{"text": self.system_instruction}]},
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600},
        }
        response = requests.post(
            f"{GEMINI_API_URL}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=45,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Pau Gemini API error {response.status_code}: {response.text[:500]}"
            )

        body = response.json()
        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError("Pau response has no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Pau response has no content parts")
        text = parts[0].get("text", "").strip()
        if not text:
            raise RuntimeError("Pau response is empty")
        return text


def generar_audio_habla(texto: str, idioma: str) -> dict[str, Any]:
    webhook = (os.environ.get("PAU_TTS_ENDPOINT") or "").strip()
    fallback_audio_url = (os.environ.get("PAU_TTS_FALLBACK_AUDIO_URL") or "").strip()
    estimated_duration_ms = max(1800, min(len(texto) * 55, 12000))

    if not webhook:
        if fallback_audio_url:
            return {
                "status": "success",
                "audio_data": fallback_audio_url,
                "duracion_animacion_ms": estimated_duration_ms,
            }
        return {
            "status": "error",
            "error": "PAU_TTS_ENDPOINT no configurado",
            "duracion_animacion_ms": estimated_duration_ms,
        }

    response = requests.post(
        webhook,
        headers={"Content-Type": "application/json"},
        json={"texto": texto, "idioma": idioma},
        timeout=60,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Pau TTS API error {response.status_code}: {response.text[:500]}")

    body = response.json()
    audio_data = body.get("audio_data") or body.get("audioUrl") or body.get("url")
    duration = int(
        body.get("duracion_animacion_ms")
        or body.get("durationMs")
        or estimated_duration_ms
    )
    if not audio_data:
        return {
            "status": "error",
            "error": "Respuesta TTS sin audio_data",
            "duracion_animacion_ms": duration,
        }
    return {
        "status": "success",
        "audio_data": audio_data,
        "duracion_animacion_ms": duration,
    }

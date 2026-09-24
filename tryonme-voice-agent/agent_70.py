"""
Agent 70 — VoiceOrchestrator: cerebro TryOnMe + Gemini Function Calling.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable

from google import genai
from google.genai import types

import prompts


@dataclass
class VoiceOrchestrator:
    name: str = "Luna"
    brand: str = "TryOnMe"
    llm: str = "gemini-1.5-flash"
    tools: dict[str, Callable[[dict[str, Any]], str]] = field(default_factory=dict)
    system_prompt: str = field(default_factory=lambda: prompts.SYSTEM_PROMPT)

    def _client(self) -> genai.Client:
        key = (
            os.environ.get("GEMINI_API_KEY", "").strip()
            or os.environ.get("GOOGLE_API_KEY", "").strip()
        )
        if not key:
            raise RuntimeError("GEMINI_API_KEY o GOOGLE_API_KEY requerido.")
        return genai.Client(api_key=key)

    def _declarations(self) -> list[dict[str, Any]]:
        from tools import TryOnMeTools

        return TryOnMeTools.declarations()

    def reply(self, transcript: str) -> str:
        """Un turno: transcripción -> Gemini + tools -> texto para Twilio <Say>."""
        t = (transcript or "").strip()
        if not t:
            return "No te he oído bien. ¿Puedes repetirlo?"

        client = self._client()
        decls = self._declarations()
        tool = types.Tool(function_declarations=decls)
        config = types.GenerateContentConfig(
            tools=[tool],
            system_instruction=self.system_prompt,
        )

        contents: list[types.Content] = [
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=(
                            f"Transcripción del cliente (voz): {t}\n"
                            "Usa herramientas si aplica. Respuesta final: 1–2 frases "
                            "cortas en español, para leer en voz alta."
                        ),
                    ),
                ],
            ),
        ]

        for _ in range(6):
            response = client.models.generate_content(
                model=self.llm,
                contents=contents,
                config=config,
            )
            cands = getattr(response, "candidates", None) or []
            if not cands:
                return "¿Puedes repetirlo con calma?"
            parts = cands[0].content.parts or []

            fcalls = [p.function_call for p in parts if getattr(p, "function_call", None)]
            texts = [p.text for p in parts if getattr(p, "text", None)]

            if not fcalls:
                reply = "".join(texts).strip()
                return reply or "¿Puedes repetirlo?"

            contents.append(cands[0].content)
            fr_parts: list[types.Part] = []
            for fc in fcalls:
                name = fc.name
                raw_args = fc.args or {}
                args = dict(raw_args) if hasattr(raw_args, "items") else {}
                fn = self.tools.get(name)
                try:
                    out = fn(args) if fn else "Esa consulta no está disponible."
                except Exception as e:
                    print(f"[Agent70] tool {name}: {e}", file=sys.stderr)
                    out = "No se pudo completar la consulta en este momento."
                fr_parts.append(
                    types.Part.from_function_response(
                        name=name,
                        response={"result": out},
                    ),
                )
            contents.append(types.Content(role="user", parts=fr_parts))

        return "Demasiados pasos seguidos. Llama o prueba en unos segundos."

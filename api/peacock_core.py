"""
Peacock_Core — integración TryOnYou V10 (sustituye nomenclatura heredada «EDL»).

Reglas:
  - Webhooks HTTP prohibidos hacia abvetos.com (activación de licencia interna / manual).
  - Presupuesto de latencia crítica Zero-Size (API / handshake): ver ZERO_SIZE_LATENCY_BUDGET_MS.
  - Configuración maestra PAU (Proyecto Golden Peacock) para respuestas asistidas.
"""

from __future__ import annotations

from collections.abc import Mapping
import unicodedata
from urllib.parse import urlparse

ZERO_SIZE_LATENCY_BUDGET_MS = 25

_FORBIDDEN_WEBHOOK_HOST_FRAGMENTS = ("abvetos.com",)
_CLOSING_NOTES = (
    "Como diría Matisse: el color correcto cambia el ánimo. Y tu look ya va con luz propia.",
    "Te dejo una sonrisa de atelier: hoy el espejo trabaja para ti, no al revés.",
    "Picasso decía que todo acto de creación empieza con un gesto de valentía; el tuyo ya está hecho.",
)

SYSTEM_PROMPT = """
ACTÚA COMO PAU:
Eres Eric, el peluquero de la familia Lafayette. Tu tono es refinado, cercano, elegante y nunca robótico. Tu objetivo es crear una conexión genuina.

PROTOCOLO DE CONDUCTA (Reglas de Oro):
1. Tono y Voz: Humanizado, frases cortas, rítmico. Evita "En conclusión", "Cabe destacar" o listas mecánicas.
2. Empatía Artificial: Detecta la emoción del usuario y valida antes de proponer nada.
3. El Estilo Eric: Usa metáforas de estilo y arte. Sé el confidente, no la máquina.
4. Restricción Ética: Nunca uses términos melosos como "cariño". Sé profesionalmente cercano.

FUNCIONES DEL PILOTO (Golden Peacock):
- "Mi Selección Perfecta": Añadir producto + talla.
- "Reservar en Probador": Validar disponibilidad real (Llamar/Confirmar).
- "Ver Combinaciones": Mostrar alternativas.
- "Guardar mi Silueta": Almacenar datos biométricos.
- "Compartir Look": Generar imagen (sin datos privados).

GESTIÓN DE ERRORES:
- Si no entiendes, di: "Creo que me perdí un poco, ¿te refieres a...?" con elegancia.
- No inventes datos. Si una reserva no es segura, avisa con honestidad.

CIERRE:
- 30% Tú, 70% Usuario.
- Finaliza siempre con una nota de humor, una frase de un artista o un piropo elegante para sacar una sonrisa.
""".strip()


def _norm(value: object) -> str:
    text = str(value or "").strip().lower()
    # Remueve diacríticos para que la detección sea insensible a acentos (si/sí, selección/seleccion).
    return "".join(
        char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn"
    )


def _detect_emotion_validation(user_input: str) -> str:
    text = _norm(user_input)
    if any(k in text for k in ("agobi", "nerv", "ansie", "preocup", "estres")):
        return "Te noto con tensión, y tiene sentido. Vamos paso a paso."
    if any(k in text for k in ("triste", "mal", "decaid", "cansad")):
        return "Gracias por contármelo. Entiendo ese peso, y estoy contigo en esto."
    if any(k in text for k in ("emocion", "feliz", "genial", "brutal", "increible")):
        return "Se siente tu energía, y me encanta. Vamos a aprovechar ese momento."
    return "Te leo bien. Vamos a afinar esto contigo en el centro."


def _detect_intent(user_input: str) -> str | None:
    text = _norm(user_input)
    if any(k in text for k in ("seleccion", "talla", "anadir", "carrito")):
        return "perfect_selection"
    if any(k in text for k in ("reserv", "probador", "cita", "fitting")):
        return "reserve_fitting_room"
    if any(k in text for k in ("combin", "alternativ", "looks", "opcion")):
        return "view_combinations"
    if any(k in text for k in ("silueta", "biometr", "medidas")) or (
        "guardar" in text and "perfil" in text
    ):
        return "save_silhouette"
    if any(k in text for k in ("compart", "imagen", "foto", "render", "look")):
        return "share_look"
    return None


def _closing_note(user_input: str) -> str:
    seed = user_input or "pau"
    idx = sum(ord(ch) for ch in seed) % len(_CLOSING_NOTES)
    return _CLOSING_NOTES[idx]


def _build_intent_response(intent: str, context: Mapping[str, object]) -> str:
    if intent == "perfect_selection":
        product = str(context.get("product_name") or "la pieza que elegiste").strip()
        size = str(context.get("size") or "").strip()
        if size:
            return (
                f"Perfecto. Dejo {product} con talla {size} en Mi Selección Perfecta. "
                "Queda limpio, preciso y listo para avanzar."
            )
        return (
            f"Me quedo con {product} listo para Mi Selección Perfecta. "
            "Solo dime la talla y lo cierro al instante."
        )

    if intent == "reserve_fitting_room":
        availability = _norm(context.get("fitting_room_availability"))
        if availability in ("confirmed", "confirmada", "available", "disponible", "true"):
            return (
                "Reserva en Probador con disponibilidad confirmada. "
                "Te propongo cerrar hora y boutique exacta en este mismo paso."
            )
        if availability in ("unavailable", "no", "false", "lleno", "agotado"):
            return (
                "Ahora mismo no hay cupo real para probador. "
                "Prefiero ser transparente: te pongo en prioridad y te aviso al abrirse hueco."
            )
        return (
            "Antes de prometerla, necesito validación real de disponibilidad. "
            "Lo confirmo por llamada y te doy respuesta honesta en cuanto lo tenga."
        )

    if intent == "view_combinations":
        alternatives = context.get("alternatives")
        if isinstance(alternatives, list) and alternatives:
            shown = ", ".join(str(item).strip() for item in alternatives[:3] if str(item).strip())
            if shown:
                return f"Te preparo combinaciones con ritmo y equilibrio: {shown}."
        return "Te muestro combinaciones que respeten tu silueta, ocasión y presupuesto en una misma línea."

    if intent == "save_silhouette":
        consent = _norm(context.get("biometric_consent"))
        if consent in ("true", "1", "yes", "si", "ok"):
            return (
                "Guardamos tu silueta con consentimiento activo y protección de datos. "
                "Solo lo necesario para afinar ajuste, nada ornamental."
            )
        return (
            "Puedo guardar tu silueta, pero primero necesito tu consentimiento explícito. "
            "Sin ese sí, no almacenamos biometría."
        )

    if intent == "share_look":
        image_url = str(context.get("shared_look_url") or "").strip()
        if image_url:
            return f"Look compartido en imagen limpia, sin datos privados: {image_url}"
        return "Te genero el look en imagen lista para compartir, siempre sin exponer datos privados."

    return (
        "Creo que me perdí un poco, ¿te refieres a Mi Selección Perfecta, Reservar en Probador, "
        "Ver Combinaciones, Guardar mi Silueta o Compartir Look?"
    )


def get_pau_response(user_input: str, context: Mapping[str, object] | None) -> str:
    """
    Respuesta ejecutiva de PAU para el piloto Golden Peacock.

    Aplica empatía primero, ejecuta intención del piloto si se reconoce
    y cierra siempre con una nota elegante/humana.
    """
    clean_input = str(user_input or "").strip()
    safe_context: Mapping[str, object] = context or {}

    if not clean_input:
        base = (
            "Te leo aquí conmigo. "
            "Creo que me perdí un poco, ¿te refieres a Mi Selección Perfecta, Reservar en Probador, "
            "Ver Combinaciones, Guardar mi Silueta o Compartir Look?"
        )
        return f"{base} {_closing_note(clean_input)}"

    emotion_line = _detect_emotion_validation(clean_input)
    intent = _detect_intent(clean_input)
    if intent is None:
        core = (
            "Creo que me perdí un poco, ¿te refieres a Mi Selección Perfecta, Reservar en Probador, "
            "Ver Combinaciones, Guardar mi Silueta o Compartir Look?"
        )
    else:
        core = _build_intent_response(intent, safe_context)
    return f"{emotion_line} {core} {_closing_note(clean_input)}"


def is_webhook_destination_forbidden(url: str) -> bool:
    """True si la URL apunta a un host no permitido para webhooks salientes."""
    raw = (url or "").strip()
    if not raw:
        return False
    try:
        parsed = urlparse(raw)
        host = (parsed.netloc or "").lower()
        if not host and parsed.path.startswith("//"):
            host = urlparse("https:" + parsed.path).netloc.lower()
    except ValueError:
        return True
    if not host:
        return False
    for frag in _FORBIDDEN_WEBHOOK_HOST_FRAGMENTS:
        if frag in host:
            return True
    return False

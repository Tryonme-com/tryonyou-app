"""
Jules — parámetros de ciclo de vida para conexiones en tiempo real (WebSocket / streaming).

Objetivo operativo: mantener el camino crítico por debajo de ~500 ms donde aplica
(handshake / primer ack hacia Twilio Media Streams u homólogos).
"""

from __future__ import annotations

# Presupuesto máximo para operaciones “críticas” (aceptar WS, primer mensaje, etc.)
WEBSOCKET_LATENCY_BUDGET_MS: int = 500

# Keep-alive recomendado para conexiones largas (Media Streams)
WEBSOCKET_PING_INTERVAL_SEC: float = 20.0
WEBSOCKET_CONNECT_TIMEOUT_SEC: float = 5.0

# Objetivo interno de primer byte de respuesta (ms) tras evento del cliente
STREAM_ACK_TARGET_MS: int = 450

# Twilio Media Streams suele JSON por texto; tamaño máximo de trama procesada en demo
MAX_WS_MESSAGE_BYTES: int = 65_536

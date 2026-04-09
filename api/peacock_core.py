"""
Peacock_Core — integración TryOnYou V10 (sustituye nomenclatura heredada «EDL»).

Reglas:
  - Webhooks HTTP prohibidos hacia abvetos.com (activación de licencia interna / manual).
  - Presupuesto de latencia crítica Zero-Size (API / handshake): ver ZERO_SIZE_LATENCY_BUDGET_MS.
  - Verificación de firma HMAC-SHA1 para webhooks entrantes (Make.com).
  - Guardia de idempotencia para prevenir procesamiento concurrente duplicado.
"""

from __future__ import annotations

import hashlib
import hmac
import threading
import time
from urllib.parse import urlparse

ZERO_SIZE_LATENCY_BUDGET_MS = 25

_FORBIDDEN_WEBHOOK_HOST_FRAGMENTS = ("abvetos.com",)


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


def verify_webhook_sha1_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
) -> bool:
    """Verifica una firma HMAC-SHA1 de un webhook entrante.

    Args:
        payload:          Cuerpo crudo de la petición (bytes).
        signature_header: Valor de la cabecera ``X-Hub-Signature`` en formato
                          ``sha1=<hex_digest>``.
        secret:           Secreto compartido configurado en el emisor del webhook.

    Returns:
        ``True`` si la firma es válida, ``False`` en cualquier otro caso.
    """
    if not payload or not signature_header or not secret:
        return False
    if not signature_header.startswith("sha1="):
        return False
    received_digest = signature_header[len("sha1="):]
    expected_digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha1,
    ).hexdigest()
    return hmac.compare_digest(received_digest.lower(), expected_digest.lower())


class IdempotencyGuard:
    """Previene el procesamiento concurrente duplicado de eventos webhook.

    Mantiene un registro en memoria de los identificadores de evento procesados
    recientemente.  Las entradas expiran después de ``ttl_seconds`` para evitar
    un crecimiento ilimitado de la memoria.

    Args:
        ttl_seconds: Tiempo de vida (segundos) de cada entrada.  Por defecto 300 s.
        max_size:    Número máximo de entradas.  Si se supera se eliminan las más
                     antiguas.  Por defecto 10 000.
    """

    def __init__(self, ttl_seconds: float = 300.0, max_size: int = 10_000) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def is_duplicate(self, event_id: str) -> bool:
        """Devuelve ``True`` si *event_id* ya fue procesado y su TTL sigue activo."""
        if not event_id:
            return False
        now = time.monotonic()
        with self._lock:
            self._evict(now)
            return event_id in self._seen

    def mark_seen(self, event_id: str) -> None:
        """Registra *event_id* como procesado."""
        if not event_id:
            return
        now = time.monotonic()
        with self._lock:
            self._evict(now)
            if len(self._seen) >= self._max_size:
                # Elimina la entrada más antigua
                oldest = min(self._seen, key=lambda k: self._seen[k])
                del self._seen[oldest]
            self._seen[event_id] = now

    def _evict(self, now: float) -> None:
        """Elimina entradas expiradas (debe llamarse con el lock adquirido)."""
        cutoff = now - self._ttl
        expired = [k for k, ts in self._seen.items() if ts < cutoff]
        for k in expired:
            del self._seen[k]

"""TryOnMe tools for Gemini function calling."""
from __future__ import annotations
from typing import Any, Callable


def consultar_stock(producto: str) -> str:
    p = (producto or "").strip() or "ese articulo"
    return f"Hay 5 unidades de {p} disponibles para probarse."


def verificar_estado_pedido(id_pedido: str) -> str:
    oid = (id_pedido or "").strip() or "desconocido"
    return f"El pedido {oid} esta en camino y llega manana."


def _stock_args(a: dict[str, Any]) -> str:
    return consultar_stock(str(a.get("producto", "")))


def _pedido_args(a: dict[str, Any]) -> str:
    return verificar_estado_pedido(str(a.get("id_pedido", "")))


TOOL_DISPATCH: dict[str, Callable[[dict[str, Any]], str]] = {
    "consultar_stock": _stock_args,
    "verificar_estado_pedido": _pedido_args,
}


class TryOnMeTools:
    @staticmethod
    def get_all() -> dict[str, Callable[[dict[str, Any]], str]]:
        return TOOL_DISPATCH

    @staticmethod
    def declarations() -> list[dict[str, Any]]:
        return [
            {
                "name": "consultar_stock",
                "description": "Consulta unidades disponibles para probarse.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "producto": {"type": "string", "description": "Producto"},
                    },
                    "required": ["producto"],
                },
            },
            {
                "name": "verificar_estado_pedido",
                "description": "Estado de envio del pedido.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id_pedido": {"type": "string", "description": "Id pedido"},
                    },
                    "required": ["id_pedido"],
                },
            },
        ]

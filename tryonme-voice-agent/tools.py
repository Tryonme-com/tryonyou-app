"""Herramientas demo para stock y pedidos (sustituir por API o base de datos real)."""

from __future__ import annotations


def consultar_stock(producto: str) -> str:
    # Aquí Cursor puede conectar con tu base de datos real
    return f"Hay 5 unidades de {producto} disponibles para probarse."


def verificar_estado_pedido(id_pedido: str) -> str:
    return f"El pedido {id_pedido} está en camino y llega mañana."


TOOL_DISPATCH: dict[str, callable] = {
    "consultar_stock": lambda args: consultar_stock(str(args.get("producto", "") or "").strip()),
    "verificar_estado_pedido": lambda args: verificar_estado_pedido(
        str(args.get("id_pedido", "") or "").strip()
    ),
}

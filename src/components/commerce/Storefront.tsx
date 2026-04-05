/**
 * Storefront — 🛍️ Tienda de Reliquias
 *
 * Fetches all published relics from the backend and renders them
 * as product cards with a "Comprar" (Buy) link to the Stripe PaymentLink.
 */

import { useState, useEffect } from "react";

interface Relic {
  id: string;
  name: string;
  description: string;
  price_cents: number | null;
  currency: string;
}

function formatPrice(cents: number | null, currency: string): string {
  if (cents === null) return "—";
  const amount = cents / 100;
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: currency.toUpperCase(),
  }).format(amount);
}

export default function Storefront() {
  const [relics, setRelics] = useState<Relic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch("/api/stripe/products");
        if (!res.ok) throw new Error("API error");
        const data = (await res.json()) as { products: Relic[] };
        setRelics(data.products);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "32px 20px", color: "#111" }}>
      <h1 style={{ fontSize: "1.6rem", fontWeight: 700, marginBottom: 24 }}>🛍️ Storefront</h1>

      {loading && (
        <p style={{ color: "#888" }}>Cargando reliquias…</p>
      )}

      {!loading && error && (
        <p style={{ color: "#c62828" }}>
          No se pudieron cargar las reliquias. Comprueba la configuración del servidor.
        </p>
      )}

      {!loading && !error && relics.length === 0 && (
        <p style={{ color: "#666" }}>
          Aún no hay reliquias publicadas.{" "}
          <span style={{ fontStyle: "italic" }}>
            Sé el primero en publicar desde el Panel de Vendedor.
          </span>
        </p>
      )}

      {!loading && !error && relics.length > 0 && (
        <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 16 }}>
          {relics.map((relic) => (
            <li
              key={relic.id}
              style={{
                background: "#f9f6ef",
                border: "1px solid #e0d4b0",
                borderRadius: 8,
                padding: "16px 20px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 12,
              }}
            >
              <div>
                <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: "1rem" }}>
                  {relic.name}
                </p>
                {relic.description && (
                  <p style={{ margin: "0 0 6px", fontSize: "0.85rem", color: "#555" }}>
                    {relic.description}
                  </p>
                )}
                <p style={{ margin: 0, fontSize: "0.9rem", fontWeight: 600, color: "#6b5b3a" }}>
                  {formatPrice(relic.price_cents, relic.currency)}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

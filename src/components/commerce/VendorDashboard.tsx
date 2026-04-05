/**
 * VendorDashboard — Panel de Control de Vendedor
 *
 * Allows a seller to:
 *   1. Check their Stripe Connect account status and start onboarding.
 *   2. Publish a "relic" (product) for sale on the storefront.
 */

import { useState, useEffect, useCallback } from "react";

interface AccountStatus {
  account_id: string;
  charges_enabled: boolean;
  payouts_enabled: boolean;
  details_submitted: boolean;
}

interface VendorDashboardProps {
  sellerId: string;
}

const ACCOUNT_ID_KEY = "tryonyou_stripe_account_id";

export default function VendorDashboard({ sellerId }: VendorDashboardProps) {
  const [accountId, setAccountId] = useState<string>(
    () => localStorage.getItem(ACCOUNT_ID_KEY) ?? "",
  );
  const [status, setStatus] = useState<AccountStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [onboarding, setOnboarding] = useState(false);

  // Publish form
  const [relicName, setRelicName] = useState("");
  const [relicDescription, setRelicDescription] = useState("");
  const [relicPrice, setRelicPrice] = useState("");
  const [publishing, setPublishing] = useState(false);
  const [publishResult, setPublishResult] = useState<string>("");

  const fetchStatus = useCallback(async (id: string) => {
    if (!id) return;
    setLoadingStatus(true);
    try {
      const res = await fetch(`/api/stripe/connect/status?account_id=${encodeURIComponent(id)}`);
      if (res.ok) {
        const data = (await res.json()) as AccountStatus;
        setStatus(data);
      } else {
        setStatus(null);
      }
    } catch {
      setStatus(null);
    } finally {
      setLoadingStatus(false);
    }
  }, []);

  useEffect(() => {
    if (accountId) void fetchStatus(accountId);
  }, [accountId, fetchStatus]);

  const handleOnboard = async () => {
    setOnboarding(true);
    try {
      const res = await fetch("/api/stripe/connect/onboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seller_id: sellerId, account_id: accountId || undefined }),
      });
      if (!res.ok) throw new Error("API error");
      const data = (await res.json()) as { account_id: string; onboarding_url: string };
      const newAccountId = data.account_id;
      localStorage.setItem(ACCOUNT_ID_KEY, newAccountId);
      setAccountId(newAccountId);
      window.location.href = data.onboarding_url;
    } catch {
      window.alert("No se pudo iniciar el proceso de onboarding. Revisa la configuración de Stripe.");
    } finally {
      setOnboarding(false);
    }
  };

  const handlePublish = async () => {
    if (!relicName.trim()) { window.alert("El nombre de la reliquia es obligatorio."); return; }
    const priceCents = Math.round(parseFloat(relicPrice) * 100);
    if (!Number.isFinite(priceCents) || priceCents <= 0) {
      window.alert("Introduce un precio válido en euros (ej: 49.99).");
      return;
    }
    setPublishing(true);
    setPublishResult("");
    try {
      const res = await fetch("/api/stripe/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          seller_id: sellerId,
          name: relicName.trim(),
          description: relicDescription.trim() || undefined,
          price_cents: priceCents,
        }),
      });
      if (!res.ok) throw new Error("API error");
      const data = (await res.json()) as { payment_link: string; name: string };
      setPublishResult(`✅ Reliquia publicada: ${data.name} — ${data.payment_link}`);
      setRelicName("");
      setRelicDescription("");
      setRelicPrice("");
    } catch {
      setPublishResult("❌ Error al publicar la reliquia. Revisa la configuración de Stripe.");
    } finally {
      setPublishing(false);
    }
  };

  const isConnected = status?.charges_enabled && status?.details_submitted;

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "32px 20px", color: "#111" }}>
      <h1 style={{ fontSize: "1.6rem", fontWeight: 700, marginBottom: 28 }}>
        🔱 Panel de Control de Vendedor
      </h1>

      {/* ── 1. Account Status ── */}
      <section
        style={{
          background: "#f9f6ef",
          border: "1px solid #e0d4b0",
          borderRadius: 8,
          padding: "20px 24px",
          marginBottom: 24,
        }}
      >
        <h3 style={{ margin: "0 0 12px", fontSize: "1rem", fontWeight: 600 }}>
          1. Estado de tu Cuenta
        </h3>

        {loadingStatus ? (
          <p style={{ color: "#888" }}>Cargando...</p>
        ) : status ? (
          <div style={{ fontSize: "0.9rem", lineHeight: 1.7 }}>
            <p>
              <strong>Pagos activados:</strong>{" "}
              {status.charges_enabled ? "✅ Sí" : "⏳ Pendiente"}
            </p>
            <p>
              <strong>Payouts activados:</strong>{" "}
              {status.payouts_enabled ? "✅ Sí" : "⏳ Pendiente"}
            </p>
            <p>
              <strong>Datos enviados a Stripe:</strong>{" "}
              {status.details_submitted ? "✅ Sí" : "⏳ Pendiente"}
            </p>
          </div>
        ) : (
          <p style={{ color: "#666", fontSize: "0.9rem" }}>
            {accountId ? "No se pudo obtener el estado de la cuenta." : "Sin cuenta vinculada."}
          </p>
        )}

        {!isConnected && (
          <button
            type="button"
            onClick={() => void handleOnboard()}
            disabled={onboarding}
            style={{
              marginTop: 16,
              padding: "10px 22px",
              background: "#D3B26A",
              color: "#111",
              border: "none",
              borderRadius: 999,
              fontSize: "0.8rem",
              fontWeight: 600,
              letterSpacing: 1,
              cursor: onboarding ? "not-allowed" : "pointer",
              opacity: onboarding ? 0.6 : 1,
            }}
          >
            {onboarding ? "Redirigiendo…" : "Conectar cuenta para cobros"}
          </button>
        )}
      </section>

      {/* ── 2. Publish Relic ── */}
      <section
        style={{
          background: "#f9f6ef",
          border: "1px solid #e0d4b0",
          borderRadius: 8,
          padding: "20px 24px",
          marginBottom: 16,
        }}
      >
        <h3 style={{ margin: "0 0 14px", fontSize: "1rem", fontWeight: 600 }}>
          2. Publicar Reliquia
        </h3>

        <input
          type="text"
          placeholder="Nombre de la reliquia"
          value={relicName}
          onChange={(e) => setRelicName(e.target.value)}
          style={inputStyle}
          aria-label="Nombre de la reliquia"
        />
        <input
          type="text"
          placeholder="Descripción (opcional)"
          value={relicDescription}
          onChange={(e) => setRelicDescription(e.target.value)}
          style={inputStyle}
          aria-label="Descripción"
        />
        <input
          type="number"
          placeholder="Precio en euros (ej: 49.99)"
          value={relicPrice}
          min="0.01"
          step="0.01"
          onChange={(e) => setRelicPrice(e.target.value)}
          style={inputStyle}
          aria-label="Precio en euros"
        />

        <button
          type="button"
          onClick={() => void handlePublish()}
          disabled={publishing}
          style={{
            marginTop: 8,
            padding: "10px 22px",
            background: publishing ? "#ccc" : "#26201A",
            color: "#fff",
            border: "none",
            borderRadius: 999,
            fontSize: "0.8rem",
            fontWeight: 600,
            letterSpacing: 1,
            cursor: publishing ? "not-allowed" : "pointer",
          }}
        >
          {publishing ? "Publicando…" : "Publicar"}
        </button>

        {publishResult && (
          <p
            style={{
              marginTop: 12,
              fontSize: "0.85rem",
              color: publishResult.startsWith("✅") ? "#2e7d32" : "#c62828",
              wordBreak: "break-all",
            }}
          >
            {publishResult}
          </p>
        )}
      </section>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  display: "block",
  width: "100%",
  padding: "9px 12px",
  marginBottom: 10,
  borderRadius: 6,
  border: "1px solid #ccc",
  fontSize: "0.9rem",
  boxSizing: "border-box",
};

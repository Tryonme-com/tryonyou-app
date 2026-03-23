import React, { useState } from "react";

const stripe4_5M = (
  (import.meta.env.VITE_STRIPE_LINK_SOVEREIGNTY_4_5M ||
    import.meta.env.VITE_STRIPE_LINK_4_5M_EUR ||
    "") + ""
).trim();
const stripe98k = (
  (import.meta.env.VITE_STRIPE_LINK_SOVEREIGNTY_98K ||
    import.meta.env.VITE_STRIPE_LINK_98K_EUR ||
    "") + ""
).trim();

export default function BalmainMirror() {
  const [status, setStatus] = useState("IDLE");
  const [payload, setPayload] = useState(null);

  const runLocalDemo = () => {
    setPayload({
      look_applied: "BALMAIN Structured Blazer",
      precision: "98.4%",
      checkout_demo_ref: "demo_checkout_balmain_local",
    });
    setStatus("SUCCESS");
  };

  const executeAgent70Snap = async () => {
    setStatus("SCANNING");
    try {
      const res = await fetch("/api/snap", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "VIP_001" }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      setPayload({
        look_applied: data.look_applied,
        precision: data.precision_achieved,
        checkout_demo_ref: data.checkout_demo_ref,
      });
      setStatus("SUCCESS");
    } catch {
      setTimeout(() => {
        setStatus("SNAP");
        setTimeout(runLocalDemo, 400);
      }, 800);
    }
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100vh", background: "#050505", color: "#fff", fontFamily: "system-ui" }}>
      <div
        style={{
          padding: "0.75rem 1rem",
          textAlign: "center",
          borderBottom: "1px solid #222",
          fontSize: "0.85rem",
        }}
      >
        <span style={{ color: "#666", marginRight: "0.5rem" }}>PCT/EP2025/067317</span>
        {stripe4_5M ? (
          <a href={stripe4_5M} style={{ color: "#C5A46D", margin: "0 0.5rem" }} rel="noreferrer" target="_blank">
            Soberanía 4,5M €
          </a>
        ) : (
          <span style={{ color: "#444", margin: "0 0.5rem" }}>4,5M € (configura VITE_STRIPE_LINK_SOVEREIGNTY_4_5M)</span>
        )}
        <span style={{ color: "#333" }}>|</span>
        {stripe98k ? (
          <a href={stripe98k} style={{ color: "#C5A46D", margin: "0 0.5rem" }} rel="noreferrer" target="_blank">
            Soberanía 98k €
          </a>
        ) : (
          <span style={{ color: "#444", margin: "0 0.5rem" }}>98k € (configura VITE_STRIPE_LINK_SOVEREIGNTY_98K)</span>
        )}
      </div>
      <div style={{ padding: "2rem", textAlign: "center" }}>
        {status === "IDLE" && <p style={{ color: "#C5A46D" }}>ESPERANDO SUJETO...</p>}
        {status === "SCANNING" && <p style={{ color: "#6ae" }}>[ JULES ] SCAN...</p>}
        {status === "SUCCESS" && payload && (
          <div>
            <h2>{payload.look_applied}</h2>
            <p style={{ color: "#C5A46D" }}>{payload.precision}</p>
            <p style={{ fontSize: "0.85rem", color: "#aaa" }}>Demo ref: {payload.checkout_demo_ref}</p>
            <button type="button" style={{ marginTop: "1rem", padding: "0.75rem 1.5rem" }} onClick={() => alert(payload.checkout_demo_ref)}>
              ADQUIRIR LOOK
            </button>
          </div>
        )}
      </div>
      {status === "IDLE" && (
        <button type="button" style={{ position: "absolute", bottom: "2rem", left: "50%", transform: "translateX(-50%)", padding: "1rem 2rem" }} onClick={executeAgent70Snap}>
          DESATAR PROTOCOLO V10
        </button>
      )}
    </div>
  );
}

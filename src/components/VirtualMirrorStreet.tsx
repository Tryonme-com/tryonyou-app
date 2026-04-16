import { useState, type ReactNode } from "react";
import { generateAdvbetQR, type AdvbetQR } from "../lib/payment";

type Props = {
  disabled: boolean;
  title: string;
  className: string;
  ariaLabel: string;
  district?: "75009" | "75004" | "";
  sessionId?: string;
  onBiometricVerify: () => Promise<boolean>;
  mirrorView: ReactNode;
};

export default function VirtualMirrorStreet({
  disabled,
  title,
  className,
  ariaLabel,
  district,
  sessionId,
  onBiometricVerify,
  mirrorView,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [qr, setQr] = useState<AdvbetQR | null>(null);

  const onSnapStreet = async () => {
    if (disabled || loading) return;
    setError("");
    setLoading(true);
    try {
      const verified = await onBiometricVerify();
      if (!verified) {
        setError("Vérification biométrique non confirmée.");
        return;
      }
      const nextQr = await generateAdvbetQR({
        district,
        sessionId,
      });
      if (!nextQr) {
        setError("Impossible de générer le QR Advbet.");
        return;
      }
      setQr(nextQr);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gap: 12, justifyItems: "center" }}>
      <button
        type="button"
        className={className}
        disabled={disabled || loading}
        onClick={() => void onSnapStreet()}
        title={title}
        aria-label={ariaLabel}
        style={{
          opacity: !disabled && !loading ? 1 : 0.55,
          cursor: !disabled && !loading ? "pointer" : "not-allowed",
        }}
      >
        {mirrorView}
      </button>

      {error ? (
        <p style={{ margin: 0, fontSize: 12, color: "#7e1d1d" }}>{error}</p>
      ) : null}

      {qr ? (
        <div
          style={{
            padding: 12,
            borderRadius: 12,
            border: "1px solid rgba(211,178,106,0.55)",
            background: "rgba(255,255,255,0.82)",
            textAlign: "center",
            maxWidth: 300,
          }}
        >
          <img
            src={qr.qrImageUrl}
            alt="QR dynamique Advbet pour finaliser The Snap"
            width={220}
            height={220}
            loading="lazy"
            style={{ borderRadius: 8 }}
          />
          <p style={{ margin: "10px 0 0", fontSize: 11, color: "#3b3227" }}>
            QR actif jusqu’à {new Date(qr.expiresAt).toLocaleTimeString()}.
          </p>
          <a
            href={qr.paymentUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "inline-block",
              marginTop: 8,
              fontSize: 12,
              textDecoration: "none",
              color: "#1f4f96",
              borderBottom: "1px solid #1f4f96",
            }}
          >
            Ouvrir le paiement Advbet
          </a>
        </div>
      ) : null}
    </div>
  );
}

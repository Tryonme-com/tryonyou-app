const GOLD = "#C5A46D";
const ANTHRACITE = "#141619";

export function PaymentTerminal() {
  return (
    <div
      style={{
        backgroundColor: ANTHRACITE,
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "serif",
        padding: "2rem",
        textAlign: "center",
      }}
    >
      <h1 style={{ color: GOLD, fontSize: "2rem", marginBottom: "1rem" }}>
        DIVINEO PARIS — Accès Réservé
      </h1>
      <p style={{ color: "#fff", fontSize: "1.1rem", maxWidth: 480, lineHeight: 1.6 }}>
        Cette application nécessite une licence active. Veuillez contacter
        l&apos;équipe Divineo pour activer votre accès.
      </p>
      <p
        style={{
          color: GOLD,
          fontSize: "0.8rem",
          marginTop: "2rem",
          opacity: 0.6,
          letterSpacing: 1,
        }}
      >
        SIREN: 943 610 196 | Patente: PCT/EP2025/067317 | © 2026 DIVINEO PARIS
      </p>
    </div>
  );
}

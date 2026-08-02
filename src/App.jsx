import React from "react";
import PoseTryOnCanvas from "./components/PoseTryOnCanvas";

export default function App() {
  return (
    <div
      style={{
        backgroundColor: "#0B0B0D",
        minHeight: "100vh",
        color: "#F5F5F5",
        padding: "24px 16px",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          fontFamily: "Georgia, serif",
          color: "#C7A86A",
          marginBottom: 8,
          fontSize: 28,
        }}
      >
        TRYONYOU — Essayage live
      </h1>
      <p style={{ textAlign: "center", opacity: 0.65, marginBottom: 24, fontSize: 14 }}>
        Overlay anclado a hombros · MediaPipe · PCT/EP2025/067317
      </p>
      <PoseTryOnCanvas />
    </div>
  );
}

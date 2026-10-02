import React from "react";
import PoseTryOnCanvas from "./components/PoseTryOnCanvas";
import StationTPage from "./pages/StationTPage";
import { GALLERY_NODES, resolveGalleryPostal } from "./lib/galleryPostal.js";

function TryOnHome() {
  const postal = resolveGalleryPostal(window.location.search);
  const node = GALLERY_NODES[postal];

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
          color: "#D4AF37",
          marginBottom: 8,
          fontSize: 28,
        }}
      >
        TRYONYOU — Essayage live
      </h1>
      <p
        id="bunker-postal-node"
        data-postal={postal}
        data-venue={node.venue}
        style={{
          textAlign: "center",
          color: "#D4AF37",
          letterSpacing: "0.12em",
          marginBottom: 8,
          fontSize: 13,
        }}
      >
        Galería sincronizada · {node.label}
      </p>
      <p style={{ textAlign: "center", opacity: 0.65, marginBottom: 24, fontSize: 14 }}>
        Overlay anclado a hombros · MediaPipe · 21 landmarks · PCT/EP2025/067317
      </p>
      <PoseTryOnCanvas />
    </div>
  );
}

export default function App() {
  const pathname = window.location.pathname.replace(/\/+$/, "") || "/";

  if (pathname === "/station-t") {
    return <StationTPage />;
  }

  return <TryOnHome />;
}

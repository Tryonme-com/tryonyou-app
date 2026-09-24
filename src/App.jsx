import React from "react";
import PoseTryOnCanvas from "./components/PoseTryOnCanvas";
import StationTPage from "./pages/StationTPage";

const GALLERY_NODES = {
  "75009": { label: "Lafayette 75009", venue: "GALERIES_LAFAYETTE" },
  "75004": { label: "Marais 75004 (BHV)", venue: "BHV_MARAIS" },
  "75011": { label: "Búnker Oberkampf 75011", venue: "BUNKER_OBERKAMPF" },
};

function readGalleryPostal() {
  const params = new URLSearchParams(window.location.search);
  const raw = (params.get("postal") || params.get("cp") || "").trim();
  return GALLERY_NODES[raw] ? raw : "75011";
}

function TryOnHome() {
  const postal = readGalleryPostal();
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
        Overlay anclado a hombros · MediaPipe · PCT/EP2025/067317
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

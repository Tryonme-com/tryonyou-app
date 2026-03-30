import React from "react";
import { JulesSovereigntyFlow } from "./components/JulesSovereigntyFlow.jsx";
import { DivineoGlobalOrchestrator } from "./components/DivineoGlobalOrchestrator.jsx";
import { VirtualMirror } from "./components/VirtualMirror.tsx";

export default function App() {
  return (
    <div className="min-h-screen bg-divineo-anthracite text-divineo-gold font-sans">
      <header className="border-b border-divineo-gold/20 bg-gradient-to-b from-divineo-anthracite to-black p-6">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-divineo-bone/70">
              TRYONME × DIVINEO — FIS V10
            </p>
            <h1 className="font-serif text-2xl font-semibold text-divineo-gold sm:text-3xl">
              Fashion Intelligence System
            </h1>
            <p className="mt-1 text-sm text-divineo-bone/80">
              Piloto Galeries Lafayette · Patente PCT/EP2025/067317 · Zero-Size
            </p>
          </div>
          <a
            href="/mirror_sanctuary_v10"
            className="text-xs text-divineo-bone/60 underline decoration-divineo-gold/30 hover:text-divineo-gold"
          >
            Mirror Sanctuary (plein écran)
          </a>
        </div>
      </header>
      <main className="mx-auto max-w-6xl space-y-10 p-6">
        <VirtualMirror />
        <JulesSovereigntyFlow />
        <DivineoGlobalOrchestrator />
      </main>
      <footer className="border-t border-divineo-gold/15 py-4 text-center text-[10px] text-divineo-bone/50">
        SIRET 94361019600017 · Soberanía 4,5M € ref. · Agente 70 despliegue
      </footer>
    </div>
  );
}

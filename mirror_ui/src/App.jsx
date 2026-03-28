import React from "react";
import { JulesSovereigntyFlow } from "./components/JulesSovereigntyFlow.jsx";
import { DivineoGlobalOrchestrator } from "./components/DivineoGlobalOrchestrator.jsx";

/** FUSIÓN TOTAL V10 OMEGA — sin bloqueos */
export default function App() {
  return (
    <div className="min-h-screen bg-black text-[#D3B26A] font-sans">
      <header className="p-6 border-b border-[#D3B26A]/20 bg-gradient-to-b from-black to-zinc-900">
        <h1 className="text-3xl font-bold tracking-tighter">DIVINEO V10 OMEGA</h1>
        <p className="text-sm opacity-70">
          Soberanía total: abvetos.com (Arquitecto) | LiveitFashion.com (Artista)
        </p>
      </header>

      <main className="container mx-auto p-4 space-y-8">
        <section className="bg-zinc-900/50 p-6 rounded-xl border border-[#D3B26A]/30">
          <h2 className="text-xl mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" aria-hidden />
            Centro de mando: el Arquitecto manda
          </h2>
          <JulesSovereigntyFlow />
        </section>

        <section>
          <DivineoGlobalOrchestrator />
        </section>
      </main>

      <footer className="p-8 text-center opacity-30 text-xs">
        Búnker de infraestructura online | Protocolo Supercommit Max · PCT/EP2025/067317
      </footer>
    </div>
  );
}

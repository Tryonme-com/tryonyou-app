import React from "react";
import BalmainMirror from "./BalmainMirror.jsx";

export function DivineoGlobalOrchestrator() {
  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-[#D3B26A]/25 bg-zinc-900/40 p-6">
        <h2 className="text-lg font-semibold text-[#D3B26A] mb-2 tracking-wide">
          Orquestador global — módulos V10
        </h2>
        <p className="text-sm text-zinc-400 mb-6 max-w-3xl">
          Unidad de producción (espejo + API local), certeza biométrica y narrativa Divineo
          en una sola capa de entrega.
        </p>
        <div className="rounded-lg border border-zinc-700/60 bg-black/30 overflow-hidden">
          <BalmainMirror />
        </div>
      </div>
    </div>
  );
}

import React from "react";

const linkClass =
  "inline-flex items-center gap-2 rounded-lg border border-[#D3B26A]/35 bg-black/40 px-4 py-3 text-sm text-[#D3B26A] hover:bg-[#D3B26A]/10 transition-colors";

export function JulesSovereigntyFlow() {
  return (
    <div className="space-y-6">
      <p className="text-sm text-zinc-400 max-w-3xl leading-relaxed">
        Flujo de soberanía Jules V10: trazabilidad operativa, dashboards y hitos alineados
        con el protocolo TryOnMe × Divineo. Sin bloqueos en la capa de entrega.
      </p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <a
          href="https://abvetos.com/"
          className={linkClass}
          rel="noreferrer"
          target="_blank"
        >
          <span className="h-2 w-2 rounded-full bg-emerald-400" aria-hidden />
          Arquitecto — abvetos.com
        </a>
        <a
          href="https://liveitfashion.com/"
          className={linkClass}
          rel="noreferrer"
          target="_blank"
        >
          <span className="h-2 w-2 rounded-full bg-amber-400" aria-hidden />
          Artista — LiveitFashion.com
        </a>
        <a
          href="https://tryonyou.org/"
          className={linkClass}
          rel="noreferrer"
          target="_blank"
        >
          <span className="h-2 w-2 rounded-full bg-[#D3B26A]" aria-hidden />
          tryonyou.org — frente público
        </a>
      </div>
      <dl className="grid gap-3 text-xs text-zinc-500 sm:grid-cols-2 border-t border-[#D3B26A]/15 pt-4">
        <div>
          <dt className="font-medium text-zinc-400">Protocolo</dt>
          <dd>V10.4 Lafayette · OMEGA</dd>
        </div>
        <div>
          <dt className="font-medium text-zinc-400">Patente (ref.)</dt>
          <dd>PCT/EP2025/067317</dd>
        </div>
      </dl>
    </div>
  );
}

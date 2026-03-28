import React, { useState } from "react";

const STEPS = [
  { id: "audit", label: "Auditoría PCT / SIRET", done: true },
  { id: "capital", label: "Bridge liquidez (Bpifrance / mesas)", done: false },
  { id: "deploy", label: "Supercommit Max → producción", done: false },
];

export function JulesSovereigntyFlow() {
  const [open, setOpen] = useState(true);

  return (
    <div className="space-y-4">
      <p className="text-sm text-[#D3B26A]/80 max-w-2xl">
        Flujo de soberanía técnica: el arquitecto fija la verdad del repo; el artista
        vive en la superficie pública. Sin bloqueos de entrega.
      </p>
      <div className="flex flex-wrap gap-4 text-sm">
        <a
          href="https://abvetos.com/"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 rounded-lg border border-[#D3B26A]/40 bg-black/40 hover:bg-[#D3B26A]/10 transition-colors"
        >
          Dashboard — abvetos.com
        </a>
        <a
          href="https://liveitfashion.com/"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 rounded-lg border border-[#D3B26A]/40 bg-black/40 hover:bg-[#D3B26A]/10 transition-colors"
        >
          Artista — LiveitFashion.com
        </a>
        <a
          href="https://tryonyou.org/"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 rounded-lg border border-[#D3B26A]/40 bg-black/40 hover:bg-[#D3B26A]/10 transition-colors"
        >
          tryonyou.org
        </a>
      </div>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="text-xs uppercase tracking-widest text-[#D3B26A]/60 hover:text-[#D3B26A]"
      >
        {open ? "Ocultar hitos" : "Ver hitos operativos"}
      </button>
      {open && (
        <ol className="list-decimal list-inside space-y-2 text-sm text-zinc-300">
          {STEPS.map((s) => (
            <li key={s.id} className={s.done ? "text-emerald-400/90" : ""}>
              <span className="mr-2">{s.done ? "✓" : "○"}</span>
              {s.label}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

/**
 * Puente estable hacia Jules (Make.com / orquestaciones: mismos nombres de campo que api/index.py).
 */

export type JulesHealth = {
  ok: boolean;
  service?: string;
  siren?: string;
  patente?: string;
  product_lane?: string;
  protocol?: string;
};

export type JulesHandshake = {
  status?: string;
  jules_msg?: string;
  protocolo?: string;
  next_step?: string;
  patente?: string;
  siren?: string;
  product_lane?: string;
};

export async function fetchJulesHealth(): Promise<JulesHealth | null> {
  try {
    const r = await fetch("/api/health", { method: "GET" });
    if (!r.ok) return null;
    return (await r.json()) as JulesHealth;
  } catch {
    return null;
  }
}

export async function postJulesHandshake(): Promise<JulesHandshake | null> {
  try {
    const r = await fetch("/api", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ping: true }),
    });
    if (!r.ok) return null;
    return (await r.json()) as JulesHandshake;
  } catch {
    return null;
  }
}

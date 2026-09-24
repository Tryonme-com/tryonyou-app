import {
  buildCoreHeaders,
  ensureMirrorSessionId,
  fetchCoreHealth,
  resolveAccountScope,
  type JulesHealth,
} from "./coreEngineClient";

export type { JulesHealth } from "./coreEngineClient";

export type JulesHandshake = {
  status?: string;
  jules_msg?: string;
  protocolo?: string;
  next_step?: string;
  patente?: string;
  siren?: string;
  product_lane?: string;
  mirror_enabled?: boolean;
};

export async function fetchJulesHealth(): Promise<JulesHealth | null> {
  return fetchCoreHealth();
}

export async function postJulesHandshake(): Promise<JulesHandshake | null> {
  try {
    const r = await fetch("/api", {
      method: "POST",
      headers: buildCoreHeaders(),
      body: JSON.stringify({
        ping: true,
        session_id: ensureMirrorSessionId(),
        account_scope: resolveAccountScope(),
      }),
      credentials: "same-origin",
    });
    if (!r.ok) return null;
    return (await r.json()) as JulesHandshake;
  } catch {
    return null;
  }
}

export type InventoryMatch = {
  match_absolute?: string;
  garment_id?: string;
  brand_line?: string;
  message?: string;
  protocol?: string;
};

export async function postMirrorSnap(
  fabricSensation: string,
  fabricFitVerdict?: string,
): Promise<(JulesHandshake & { inventory_match?: InventoryMatch }) | null> {
  try {
    const r = await fetch("/api/v1/mirror/snap", {
      method: "POST",
      headers: buildCoreHeaders(),
      body: JSON.stringify({
        ping: true,
        session_id: ensureMirrorSessionId(),
        account_scope: resolveAccountScope(),
        fabric_sensation: fabricSensation,
        fabric_fit_verdict: fabricFitVerdict ?? "",
      }),
      credentials: "same-origin",
    });
    if (!r.ok) return null;
    return (await r.json()) as JulesHandshake & {
      inventory_match?: InventoryMatch;
    };
  } catch {
    return null;
  }
}

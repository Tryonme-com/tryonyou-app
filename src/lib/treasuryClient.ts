/**
 * Treasury & Territory API client — V11 Expansion.
 * Payout monitoring, capital blindaje and multi-node licensing.
 *
 * SIRET 94361019600017 | PCT/EP2025/067317
 */

export type TreasuryStatus = {
  entity: string;
  siret: string;
  capital_eur: number;
  total_payouts_eur: number;
  reserve_eur: number;
  payout_budget_eur: number;
  payout_slots: number;
  payout_amount_per_slot_eur: number;
  payouts_executed: number;
  capital_label: string;
  bank: string;
  ts: string;
};

export type PayoutEntry = {
  amount_eur: number;
  recipient: string;
  concept: string;
  ts: string;
};

export type TerritoryNode = {
  id: string;
  name: string;
  city: string;
  district: string;
  status: "ACTIVE" | "PENDING_LICENCE";
  licence_eur: number;
  confirmed: boolean;
};

export type TerritorySummary = {
  total_nodes: number;
  active_nodes: number;
  pending_nodes: number;
  active_names: string[];
  pending_names: string[];
  confirmed_revenue_eur: number;
  pending_revenue_eur: number;
  expansion_target_eur: number;
  licence_fee_eur: number;
};

export type NodeContract = {
  ref: string;
  node_id: string;
  node_name: string;
  total_licence_eur: number;
  status: string;
};

export async function fetchTreasuryStatus(): Promise<TreasuryStatus | null> {
  try {
    const r = await fetch("/api/v1/treasury/status");
    if (!r.ok) return null;
    const j = (await r.json()) as TreasuryStatus & { status: string };
    return j.status === "ok" ? j : null;
  } catch {
    return null;
  }
}

export async function fetchTerritoryNodes(): Promise<{
  nodes: TerritoryNode[];
  summary: TerritorySummary;
} | null> {
  try {
    const r = await fetch("/api/v1/territory/nodes");
    if (!r.ok) return null;
    const j = (await r.json()) as {
      status: string;
      nodes: TerritoryNode[];
      summary: TerritorySummary;
    };
    return j.status === "ok" ? { nodes: j.nodes, summary: j.summary } : null;
  } catch {
    return null;
  }
}

export async function generateNodeContract(
  nodeId: string,
): Promise<NodeContract | null> {
  try {
    const r = await fetch("/api/v1/territory/contracts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ node_id: nodeId }),
    });
    if (!r.ok) return null;
    const j = (await r.json()) as { status: string; contract: NodeContract };
    return j.status === "ok" ? j.contract : null;
  } catch {
    return null;
  }
}

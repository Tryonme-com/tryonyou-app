/**
 * Brand Outreach Campaign API client.
 * Manages the 60-brand email campaign via Resend.
 *
 * SIRET 94361019600017 | PCT/EP2025/067317
 */

export type CampaignStatus = {
  configured: boolean;
  total_brands: number;
  emails_sent: number;
  emails_failed: number;
  log_entries: number;
};

export type BrandEntry = {
  name: string;
  contact_email: string;
};

export type SendResult = {
  ok: boolean;
  brand: string;
  to?: string;
  error?: string;
  resend_response?: Record<string, unknown>;
};

export type CampaignResult = {
  campaign_id: string;
  total: number;
  sent: number;
  failed: number;
  errors: { brand: string; error: unknown }[];
  details: SendResult[];
};

export type LogEntry = {
  action: string;
  brand?: string;
  to?: string;
  status?: string;
  resend_id?: string;
  timestamp?: string;
  campaign_id?: string;
  error?: string;
};

export async function fetchCampaignStatus(): Promise<CampaignStatus | null> {
  try {
    const r = await fetch("/api/v1/campaign/status");
    if (!r.ok) return null;
    return (await r.json()) as CampaignStatus;
  } catch {
    return null;
  }
}

export async function fetchBrandsList(): Promise<{ brands: BrandEntry[]; total: number } | null> {
  try {
    const r = await fetch("/api/v1/campaign/brands");
    if (!r.ok) return null;
    return (await r.json()) as { brands: BrandEntry[]; total: number };
  } catch {
    return null;
  }
}

export async function sendBrandEmail(
  brand: string,
  email: string,
  subject?: string,
): Promise<SendResult> {
  const r = await fetch("/api/v1/campaign/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brand, email, subject }),
  });
  return (await r.json()) as SendResult;
}

export async function executeCampaign(
  brands?: string[],
  contacts?: Record<string, string>,
): Promise<CampaignResult> {
  const r = await fetch("/api/v1/campaign/execute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ brands, contacts }),
  });
  return (await r.json()) as CampaignResult;
}

export async function fetchCampaignLog(): Promise<LogEntry[]> {
  try {
    const r = await fetch("/api/v1/campaign/log");
    if (!r.ok) return [];
    const j = (await r.json()) as { entries: LogEntry[]; total: number };
    return j.entries;
  } catch {
    return [];
  }
}

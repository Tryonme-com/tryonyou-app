export type AccountScope = "personal" | "empresa" | "admin";

export type JulesHealth = {
  ok: boolean;
  service?: string;
  product_lane?: string;
  protocol?: string;
  mirror_enabled?: boolean;
  kill_switch?: {
    state?: "on" | "off";
    updated_at?: string;
    updated_by?: string;
  };
};

export type CoreTrace = {
  event_id?: string;
  session_id?: string;
  account_scope?: AccountScope;
  commission_rate?: number;
  commission_audit_eur?: number;
  db_persisted?: boolean;
  created_at?: string;
};

export type ModelAccessTokenResponse = {
  ok: boolean;
  access_token?: string;
  session_id?: string;
  protocol?: string;
  status?: string;
  message?: string;
  validation?: {
    qualified?: boolean;
    combined_total_eur?: number;
    threshold_eur?: number;
  };
  trace?: CoreTrace;
};

const SESSION_KEY = "tryonyou:jules:mirror-session-id";

function normalizeScope(raw: string): AccountScope {
  const value = raw.trim().toLowerCase();
  if (["admin", "administrator", "root", "owner"].includes(value)) {
    return "admin";
  }
  if (["empresa", "business", "company", "enterprise", "corp"].includes(value)) {
    return "empresa";
  }
  return "personal";
}

function randomSessionId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return `jules_${crypto.randomUUID().replaceAll("-", "")}`;
  }
  return `jules_${Math.random().toString(36).slice(2)}${Date.now().toString(36)}`;
}

export function ensureMirrorSessionId(): string {
  if (typeof window === "undefined") return randomSessionId();
  const current = window.sessionStorage.getItem(SESSION_KEY)?.trim();
  if (current) return current;
  const created = randomSessionId();
  window.sessionStorage.setItem(SESSION_KEY, created);
  return created;
}

export function resolveAccountScope(): AccountScope {
  if (typeof window === "undefined") return "personal";
  const maybeUserCheck = window as Window & {
    UserCheck?: {
      role?: string;
      account_scope?: string;
      accountEnvironment?: string;
      contract?: string;
    };
  };
  const uc = maybeUserCheck.UserCheck;
  if (uc?.account_scope) return normalizeScope(uc.account_scope);
  if (uc?.accountEnvironment) return normalizeScope(uc.accountEnvironment);
  if (uc?.role) return normalizeScope(uc.role);
  try {
    const url = new URL(window.location.href);
    const fromQuery = url.searchParams.get("account_scope") || url.searchParams.get("scope") || "";
    if (fromQuery) return normalizeScope(fromQuery);
  } catch {
    /* no-op */
  }
  return "personal";
}

export function buildCoreHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    "X-Jules-Session-Id": ensureMirrorSessionId(),
    "X-Jules-Account-Scope": resolveAccountScope(),
  };
}

export async function trackCoreEvent(
  eventType: string,
  payload: Record<string, unknown> = {},
): Promise<CoreTrace | null> {
  try {
    const response = await fetch("/api/v1/core/trace", {
      method: "POST",
      headers: buildCoreHeaders(),
      body: JSON.stringify({
        event_type: eventType,
        source: "tryonyou_frontend",
        session_id: ensureMirrorSessionId(),
        account_scope: resolveAccountScope(),
        ...payload,
      }),
      credentials: "same-origin",
    });
    if (!response.ok) return null;
    const data = (await response.json()) as { trace?: CoreTrace };
    return data.trace ?? null;
  } catch {
    return null;
  }
}

export async function fetchModelAccessToken(
  payload: Record<string, unknown> = {},
): Promise<ModelAccessTokenResponse | null> {
  try {
    const response = await fetch("/api/v1/core/model-access-token", {
      method: "POST",
      headers: buildCoreHeaders(),
      body: JSON.stringify({
        session_id: ensureMirrorSessionId(),
        account_scope: resolveAccountScope(),
        ...payload,
      }),
      credentials: "same-origin",
    });
    const data = (await response.json().catch(() => null)) as ModelAccessTokenResponse | null;
    return data;
  } catch {
    return null;
  }
}

export async function fetchCoreHealth(): Promise<JulesHealth | null> {
  try {
    const response = await fetch("/api/health", {
      method: "GET",
      credentials: "same-origin",
    });
    if (!response.ok) return null;
    return (await response.json()) as JulesHealth;
  } catch {
    return null;
  }
}

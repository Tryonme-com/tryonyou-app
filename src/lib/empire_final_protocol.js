const SOUVERAINETE_STORAGE_KEY = "tryonyou_souverainete_state_v1";
const SOUVERAINETE_CHIP_ID = "souverainete-status-chip";
const RUNTIME_STYLE_ID = "empire-final-protocol-style";

function nowIso() {
  return new Date().toISOString();
}

function generateFlowToken() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `flow-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`;
}

function injectRuntimeStyles() {
  if (document.getElementById(RUNTIME_STYLE_ID)) return;
  const style = document.createElement("style");
  style.id = RUNTIME_STYLE_ID;
  style.textContent = `
body[data-anthracite-seal="1"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9997;
  background:
    radial-gradient(circle at 24% 22%, rgba(212, 175, 55, 0.2), transparent 52%),
    radial-gradient(circle at 72% 18%, rgba(224, 214, 194, 0.08), transparent 56%),
    radial-gradient(circle at 50% 82%, rgba(29, 31, 35, 0.88), rgba(11, 12, 14, 0.96) 62%);
  opacity: 0;
  animation: anthraciteSealReveal 460ms ease forwards;
}

#${SOUVERAINETE_CHIP_ID} {
  position: fixed;
  right: 18px;
  bottom: 86px;
  z-index: 9998;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.6);
  background: rgba(13, 14, 18, 0.86);
  color: #d4af37;
  font-family: "Cinzel", Georgia, serif;
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(6px);
}

#${SOUVERAINETE_CHIP_ID}[data-active="1"] {
  color: #f5f3ee;
  border-color: rgba(212, 175, 55, 0.9);
  background:
    radial-gradient(circle at 18% 20%, rgba(212, 175, 55, 0.35), rgba(15, 16, 20, 0.94) 58%);
  box-shadow:
    0 0 0 1px rgba(212, 175, 55, 0.22),
    0 14px 40px rgba(212, 175, 55, 0.24);
}

@keyframes anthraciteSealReveal {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
`;
  document.head.appendChild(style);
}

function ensureSouveraineteChip() {
  injectRuntimeStyles();
  let chip = document.getElementById(SOUVERAINETE_CHIP_ID);
  if (!chip) {
    chip = document.createElement("div");
    chip.id = SOUVERAINETE_CHIP_ID;
    chip.textContent = "SOUVERAINETÉ : 0";
    document.body.appendChild(chip);
  }
  return chip;
}

function readStoredState() {
  try {
    const raw = window.localStorage.getItem(SOUVERAINETE_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") return parsed;
  } catch {
    // no-op
  }
  return null;
}

function writeStoredState(nextState) {
  try {
    window.localStorage.setItem(SOUVERAINETE_STORAGE_KEY, JSON.stringify(nextState));
  } catch {
    // no-op
  }
}

function updateChipFromState(active) {
  const chip = ensureSouveraineteChip();
  chip.textContent = active ? "SOUVERAINETÉ : 1" : "SOUVERAINETÉ : 0";
  if (active) chip.setAttribute("data-active", "1");
  else chip.removeAttribute("data-active");
}

export function resolveStripeHref(fallbackHref = "") {
  const fromWindow = (window.__DIVINEO_CHECKOUT_URL__ || "").trim();
  if (fromWindow) return fromWindow;
  return (fallbackHref || "").trim();
}

export async function registerPaymentIntent({ flowToken, checkoutUrl, buttonId, source }) {
  const payload = {
    flow_token: flowToken || "",
    checkout_url: checkoutUrl || "",
    button_id: buttonId || "tryonyou-pay-button",
    source: source || "index_html_shell",
    protocol: "Pau Emotional Intelligence",
    ui_theme: "Sello de Lujo: Antracita",
  };
  try {
    await fetch("/api/v1/empire/payment-intent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    // no-op: checkout must remain non-blocking
  }
}

export async function registerPaymentSuccess({ flowToken, sessionId }) {
  const payload = {
    flow_token: flowToken || "",
    session_id: sessionId || "",
    source: "frontend_success_callback",
    protocol: "empire_final_protocol",
  };
  try {
    await fetch("/api/v1/empire/payment-success", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch {
    // no-op: UI state should still update
  }
}

export async function executePauSnap({ trigger = "tryonyou-pay-button" } = {}) {
  const flowToken = generateFlowToken();
  window.__TRYONYOU_LAST_FLOW_TOKEN__ = flowToken;
  document.body.setAttribute("data-anthracite-seal", "1");
  window.dispatchEvent(
    new CustomEvent("tryonyou:pau-emotional-intelligence", {
      detail: {
        phase: "scan_to_payment",
        trigger,
        flowToken,
        ts: nowIso(),
      },
    }),
  );
  await new Promise((resolve) => window.setTimeout(resolve, 420));
  return { flowToken, anthraciteSeal: true };
}

export function markSouverainetePaid({ source = "runtime", flowToken = "", sessionId = "" } = {}) {
  const state = {
    active: true,
    source,
    flowToken,
    sessionId,
    activatedAt: nowIso(),
  };
  writeStoredState(state);
  document.documentElement.setAttribute("data-souverainete", "1");
  updateChipFromState(true);
  window.dispatchEvent(
    new CustomEvent("tryonyou:souverainete-updated", {
      detail: state,
    }),
  );
}

export function hydrateSouveraineteFromUrl() {
  const stored = readStoredState();
  if (stored?.active) {
    document.documentElement.setAttribute("data-souverainete", "1");
    updateChipFromState(true);
  } else {
    updateChipFromState(false);
  }

  const params = new URLSearchParams(window.location.search);
  const inauguration = (params.get("inauguration") || "").toLowerCase();
  const paymentStatus = (params.get("payment_status") || "").toLowerCase();
  const sessionId = (params.get("session_id") || "").trim();
  const flowToken = (params.get("flow_token") || window.__TRYONYOU_LAST_FLOW_TOKEN__ || "").trim();
  const succeeded =
    inauguration === "merci" ||
    paymentStatus === "success" ||
    (sessionId.length > 0 && (inauguration === "success" || paymentStatus === "paid"));

  if (succeeded) {
    markSouverainetePaid({
      source: "stripe_success_url",
      flowToken,
      sessionId,
    });
    void registerPaymentSuccess({ flowToken, sessionId });
  }
}

export function bootstrapEmpireFinalProtocol() {
  hydrateSouveraineteFromUrl();
}

window.empireFinalProtocol = {
  bootstrapEmpireFinalProtocol,
  executePauSnap,
  markSouverainetePaid,
  hydrateSouveraineteFromUrl,
  resolveStripeHref,
  registerPaymentIntent,
  registerPaymentSuccess,
};

bootstrapEmpireFinalProtocol();

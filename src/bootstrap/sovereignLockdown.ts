const TARGET_HOST_FRAGMENTS = ["lafayette", "haussmann", "75009"];
const LOCKDOWN_ID = "tryonyou-sovereign-lockdown";

function hostMatchesPolicy(): boolean {
  const host = (window.location.hostname || "").toLowerCase();
  return TARGET_HOST_FRAGMENTS.some((fragment) => host.includes(fragment));
}

function isPostalBypassEnabled(): boolean {
  try {
    const u = new URL(window.location.href);
    const q = (u.searchParams.get("postal") || u.searchParams.get("cp") || "").trim();
    if (q === "75009" || q === "75004") return true;
  } catch {
    /* no-op */
  }
  const globalPostal = String(window.__TRYONYOU_POSTAL__ || "").trim();
  return globalPostal === "75009" || globalPostal === "75004";
}

function renderLockdownOverlay(): void {
  if (document.getElementById(LOCKDOWN_ID)) return;

  const overlay = document.createElement("div");
  overlay.id = LOCKDOWN_ID;
  overlay.setAttribute("role", "alert");
  overlay.style.position = "fixed";
  overlay.style.inset = "0";
  overlay.style.zIndex = "999999";
  overlay.style.display = "flex";
  overlay.style.justifyContent = "center";
  overlay.style.alignItems = "center";
  overlay.style.background = "linear-gradient(135deg, #050505 0%, #111 100%)";
  overlay.style.color = "#D4AF37";
  overlay.style.padding = "32px";
  overlay.style.fontFamily = "Georgia, serif";

  const panel = document.createElement("div");
  panel.style.maxWidth = "920px";
  panel.style.border = "3px solid #ff4444";
  panel.style.borderRadius = "6px";
  panel.style.padding = "28px";
  panel.style.background = "#000";
  panel.style.boxShadow = "0 0 80px rgba(255,0,0,0.35)";

  const title = document.createElement("h1");
  title.textContent = "ACCÈS RÉVOQUÉ";
  title.style.color = "#ff4444";
  title.style.margin = "0 0 12px";
  title.style.letterSpacing = "6px";

  const detail = document.createElement("p");
  detail.textContent =
    "Violation contractuelle détectée. Régularisation requise avant réactivation du moteur Zero-Size.";
  detail.style.margin = "0 0 16px";
  detail.style.lineHeight = "1.5";
  detail.style.color = "#ddd";

  const debt = document.createElement("p");
  debt.textContent = "Montant de régularisation: 33.200 € TTC";
  debt.style.margin = "0";
  debt.style.fontSize = "1.4rem";
  debt.style.color = "#fff";

  panel.append(title, detail, debt);
  overlay.appendChild(panel);
  document.body.appendChild(overlay);
}

export function applySovereignLockdownIfNeeded(): void {
  if (typeof window === "undefined" || typeof document === "undefined") return;
  if (!hostMatchesPolicy()) return;
  if (isPostalBypassEnabled()) return;
  window.setTimeout(() => {
    if (!isPostalBypassEnabled()) {
      renderLockdownOverlay();
    }
  }, 800);
}

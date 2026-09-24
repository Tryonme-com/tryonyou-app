/**
 * Espejo Digital → API Flask (Vercel) → Make.com.
 * URL del endpoint vía env; sin datos inventados en el payload.
 */

export type MirrorDigitalEventName = "balmain_click" | "reserve_fitting_click";

function resolveMirrorDigitalEventUrl(): string {
  const raw = (import.meta.env.VITE_MIRROR_DIGITAL_EVENT_URL as string | undefined)?.trim();
  if (raw) {
    return raw.replace(/\/$/, "");
  }
  return "/api/mirror_digital_event";
}

/**
 * POST no bloqueante. Errores de red → se ignoran para no romper la UI.
 */
export async function postMirrorDigitalEvent(
  event: MirrorDigitalEventName,
  meta: Record<string, unknown> = {},
): Promise<void> {
  const url = resolveMirrorDigitalEventUrl();
  const payload = {
    event,
    source: "tryonyou_mirror",
    meta,
  };
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      credentials: "same-origin",
    });
  } catch {
    /* offline / CORS en preview local sin API */
  }
}

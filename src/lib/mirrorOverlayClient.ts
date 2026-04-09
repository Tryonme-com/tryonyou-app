export type MirrorOverlayPayload = {
  shoulder_w_px?: number;
  hip_y_px?: number;
  fit_score_seed?: number;
  frame_spec?: {
    w?: number;
    h?: number;
  };
  shoulder_est?: number;
  waist_est?: number;
  fabric_key?: string;
  fabric_fit_verdict?: string;
  fabric_sensation?: string;
};

export type MirrorOverlayResult = {
  status?: string;
  protocol?: string;
  selected_garment?: {
    id?: string;
    brand?: string;
    name?: string;
    image_url?: string;
    color_hex?: string;
    confidence?: number;
  };
  fit_report?: {
    fit_score?: number;
    verdict?: string;
  };
  inventory_match?: {
    garment_id?: string;
    brand_line?: string;
  };
  overlay?: {
    color_hint?: string;
    alpha?: number;
    label?: string;
    garment_id?: string;
    brand_line?: string;
  };
};

export async function postMirrorOverlaySelect(
  payload: MirrorOverlayPayload,
): Promise<MirrorOverlayResult | null> {
  try {
    const r = await fetch("/api/v1/mirror/overlay", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) return null;
    return (await r.json()) as MirrorOverlayResult;
  } catch {
    return null;
  }
}

/**
 * Live Lead Scoring — detects VIP visitors from Inditex or BPI.
 *
 * Detection sources (in priority order):
 *  1. URL query param  ?ref=<company>  or  ?utm_source=<company>
 *  2. document.referrer hostname
 *
 * Returns a LeadScore object that the app uses to activate the VIP experience.
 */

export type VipBrand = "inditex" | "bpi" | null;

export type LeadScore = {
  isVip: boolean;
  brand: VipBrand;
  /** Human-readable label shown in the VIP banner */
  label: string;
};

const VIP_BRANDS: { pattern: RegExp; brand: VipBrand; label: string }[] = [
  {
    pattern: /inditex/i,
    brand: "inditex",
    label: "Inditex",
  },
  {
    /** Matches bpi, bpifrance, bpi-group, mybpi, etc. */
    pattern: /bpi/i,
    brand: "bpi",
    label: "BPI France",
  },
];

function matchBrand(value: string): { brand: VipBrand; label: string } | null {
  for (const entry of VIP_BRANDS) {
    if (entry.pattern.test(value)) {
      return { brand: entry.brand, label: entry.label };
    }
  }
  return null;
}

export function detectLeadScore(): LeadScore {
  const noVip: LeadScore = { isVip: false, brand: null, label: "" };

  if (typeof window === "undefined") return noVip;

  // 1. Query params: ?ref=inditex  |  ?utm_source=bpifrance  |  ?company=bpi
  try {
    const params = new URLSearchParams(window.location.search);
    for (const key of ["ref", "utm_source", "source", "company", "from"]) {
      const val = params.get(key) ?? "";
      if (val) {
        const hit = matchBrand(val);
        if (hit) return { isVip: true, ...hit };
      }
    }
  } catch {
    /* ignore */
  }

  // 2. document.referrer hostname
  try {
    const ref = document.referrer;
    if (ref) {
      const hostname = new URL(ref).hostname;
      const hit = matchBrand(hostname);
      if (hit) return { isVip: true, ...hit };
    }
  } catch {
    /* ignore */
  }

  return noVip;
}

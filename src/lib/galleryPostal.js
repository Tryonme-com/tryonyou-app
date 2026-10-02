/** Nodos de galería: Lafayette, Marais y búnker Oberkampf. */
export const GALLERY_NODES = {
  "75009": { label: "Lafayette 75009", venue: "GALERIES_LAFAYETTE" },
  "75004": { label: "Marais 75004 (BHV)", venue: "BHV_MARAIS" },
  "75011": { label: "Búnker Oberkampf 75011", venue: "BUNKER_OBERKAMPF" },
};

/**
 * Resuelve el código postal de la galería.
 * Sin parámetro, o con un código desconocido, la galería queda en Oberkampf 75011.
 * @param {string} search
 * @returns {"75009" | "75004" | "75011"}
 */
export function resolveGalleryPostal(search = "") {
  const query = search.startsWith("?") ? search.slice(1) : search;
  const params = new URLSearchParams(query);
  const raw = (params.get("postal") || params.get("cp") || "").trim();
  if (Object.prototype.hasOwnProperty.call(GALLERY_NODES, raw)) {
    return raw;
  }
  return "75011";
}

/**
 * Carga nina_perfecta_mesh.json usando el body de fetch como ReadableStream
 * (chunks hasta completar; luego JSON.parse). Archivos ~111MB: usar CDN/Storage con CORS.
 */
export async function loadNinaMeshFromResponseStream(url: string): Promise<unknown> {
  const res = await fetch(url, { credentials: "omit" });
  if (!res.ok) throw new Error(`Mesh HTTP ${res.status}`);
  const body = res.body;
  if (!body) {
    const text = await res.text();
    return JSON.parse(text) as unknown;
  }
  const reader = body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value) {
      chunks.push(value);
      total += value.byteLength;
    }
  }
  const merged = new Uint8Array(total);
  let offset = 0;
  for (const c of chunks) {
    merged.set(c, offset);
    offset += c.byteLength;
  }
  const text = new TextDecoder("utf-8").decode(merged);
  return JSON.parse(text) as unknown;
}

/** URL pública (Storage/CDN) del JSON de malla; vacío hasta configurar. */
export function meshUrlFromEnv(): string | null {
  const u = (import.meta.env.VITE_NINA_MESH_URL as string | undefined)?.trim();
  return u || null;
}

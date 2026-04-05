/** 🛡️ STREAM DE CERTEZA BIOMÉTRICA - 111MB
 * PATENTE: PCT/EP2025/067317
 */
export const fetchSovereignMesh = async (onProgress: (pct: number) => void): Promise<Uint8Array> => {
  const response = await fetch(import.meta.env.VITE_MESH_URL);
  if (!response.ok) {
    throw new Error(`fetchSovereignMesh: HTTP ${response.status} ${response.statusText}`);
  }
  if (!response.body) {
    throw new Error('fetchSovereignMesh: response body is not readable');
  }

  const reader = response.body.getReader();
  const contentLength = +(response.headers.get('Content-Length') ?? '0');

  const chunks: Uint8Array[] = [];
  let receivedLength = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    receivedLength += value.length;
    if (contentLength > 0) {
      onProgress((receivedLength / contentLength) * 100);
    }
  }

  const mesh = new Uint8Array(receivedLength);
  let offset = 0;
  for (const chunk of chunks) {
    mesh.set(chunk, offset);
    offset += chunk.length;
  }

  console.log("PA, PA, PA - MALLA DE 111MB CARGADA.");
  return mesh;
};

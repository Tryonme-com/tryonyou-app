/** 🛡️ STREAM DE CERTEZA BIOMÉTRICA - 111MB
 * PATENTE: PCT/EP2025/067317
 */
export const fetchSovereignMesh = async (onProgress: (pct: number) => void): Promise<void> => {
  const response = await fetch(import.meta.env.VITE_MESH_URL);
  const reader = response.body!.getReader();
  const contentLength = +response.headers.get('Content-Length')!;

  let receivedLength = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    receivedLength += value.length;
    if (contentLength > 0) {
      onProgress((receivedLength / contentLength) * 100);
    }
  }
  console.log("PA, PA, PA - MALLA DE 111MB CARGADA.");
};

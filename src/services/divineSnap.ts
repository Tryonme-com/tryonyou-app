/**
 * INTERCEPTOR DE SOBERANÍA JULES V10
 * Ejecuta el snap biométrico contra la API Cloud.
 */

export interface DivineSnapResponse {
  status: string;
  flow_token?: string;
  message?: string;
  [key: string]: unknown;
}

export const executeDivineSnap = async (
  identityColor: string,
): Promise<DivineSnapResponse> => {
  const serverUrl = import.meta.env.VITE_SERVER_URL as string | undefined;
  const apiKey = import.meta.env.VITE_JULES_API_KEY as string | undefined;

  if (!serverUrl) throw new Error("VITE_SERVER_URL is not configured.");
  if (!apiKey) throw new Error("VITE_JULES_API_KEY is not configured.");

  const response = await fetch(`${serverUrl}/api/snap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ color: identityColor, protocol: "PHRYGIAN" }),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`Server error (${response.status}): ${detail}`);
  }

  return (await response.json()) as DivineSnapResponse;
};


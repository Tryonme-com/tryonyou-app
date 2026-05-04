/**
 * INTERCEPTOR DE SOBERANÍA JULES V10
 * Ejecuta el snap biométrico contra la API Cloud.
 */

export const executeDivineSnap = async (identityColor: string): Promise<unknown> => {
  const response = await fetch(`${import.meta.env.VITE_SERVER_URL}/api/snap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_JULES_API_KEY}`,
    },
    body: JSON.stringify({ color: identityColor, protocol: "PHRYGIAN" }),
  });

  if (!response.ok) throw new Error("VULGARIZACIÓN DETECTADA EN EL SERVIDOR.");
  return await response.json();
};

/**
 * TRYONYOU V11 — Armario Solidario (AutoDonate)
 * Sincronización automática de prendas donadas.
 * 
 * Cuando un usuario compra una prenda nueva con TryOnYou,
 * el sistema sugiere donar la prenda antigua equivalente
 * a asociaciones solidarias verificadas.
 */

const SOLIDARITY_PARTNERS = [
  { id: "emmaus", name: "Emmaüs", city: "Paris", verified: true },
  { id: "secours-pop", name: "Secours Populaire", city: "Paris", verified: true },
  { id: "croix-rouge", name: "Croix-Rouge Française", city: "National", verified: true },
  { id: "vestiboutique", name: "La Vestiboutique", city: "Paris 9e", verified: true },
];

/**
 * Sugiere donación basada en la compra realizada.
 * @param {Object} purchasedGarment - Prenda comprada
 * @param {Object} userWardrobe - Armario del usuario (opcional)
 * @returns {Object} Sugerencia de donación
 */
export function suggestDonation(purchasedGarment, userWardrobe) {
  const category = purchasedGarment.category || "Vêtement";
  
  // Buscar prenda similar en el armario del usuario
  let donationCandidate = null;
  if (userWardrobe && userWardrobe.items) {
    donationCandidate = userWardrobe.items.find(
      (item) => item.category === category && item.wearCount > 20
    );
  }

  const partner = SOLIDARITY_PARTNERS[Math.floor(Math.random() * SOLIDARITY_PARTNERS.length)];

  return {
    suggestion: donationCandidate
      ? `Vous venez d'acquérir un(e) ${category}. Votre ${donationCandidate.name} pourrait faire le bonheur de quelqu'un.`
      : `Chaque achat est une opportunité de partager. Pensez à donner un vêtement que vous ne portez plus.`,
    partner,
    category,
    impactMessage: "1 vêtement donné = 1 sourire. L'élégance se partage.",
    donationUrl: `https://tryonyou.app/donate?partner=${partner.id}&category=${encodeURIComponent(category)}`,
    timestamp: Date.now(),
  };
}

/**
 * Registra una donación en el sistema.
 * @param {Object} donation - {userId, garmentId, partnerId}
 * @returns {Object} Confirmación
 */
export function registerDonation({ userId, garmentId, partnerId }) {
  const partner = SOLIDARITY_PARTNERS.find((p) => p.id === partnerId);
  
  return {
    success: true,
    donationId: `DON-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    partner: partner?.name || partnerId,
    message: `Merci pour votre générosité. ${partner?.name || "Notre partenaire"} recevra votre don.`,
    badge: "DONATEUR SOLIDAIRE",
    timestamp: Date.now(),
  };
}

/**
 * Estadísticas de impacto solidario.
 * @param {Array} donations - Lista de donaciones
 * @returns {Object} Métricas de impacto
 */
export function computeSolidarityImpact(donations) {
  const total = donations?.length || 0;
  const byPartner = {};
  
  (donations || []).forEach((d) => {
    byPartner[d.partnerId] = (byPartner[d.partnerId] || 0) + 1;
  });

  return {
    totalDonations: total,
    byPartner,
    co2Saved: total * 12, // ~12kg CO2 par vêtement réutilisé
    waterSaved: total * 2700, // ~2700L d'eau par vêtement
    message: total > 0
      ? `${total} vêtement(s) donné(s). ${total * 12}kg de CO₂ économisés.`
      : "Commencez votre impact solidaire aujourd'hui.",
  };
}

export { SOLIDARITY_PARTNERS };

export default {
  suggestDonation,
  registerDonation,
  computeSolidarityImpact,
  SOLIDARITY_PARTNERS,
};

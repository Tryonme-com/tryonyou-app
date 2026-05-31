/** Persona PAU — sellos de poder y copy emocional (Divineo V11). */

export const PAU_POWER_PHRASES = ["¡A fuego!", "¡Boom!", "¡Vivido!"] as const;

export function pauPowerSeal(): string {
  const i = Math.floor(Math.random() * PAU_POWER_PHRASES.length);
  return PAU_POWER_PHRASES[i] ?? "¡Vivido!";
}

/** Anexa un sello PAU a mensajes de éxito hacia el usuario. */
export function withPauSeal(message: string): string {
  const t = message.trim();
  if (!t) return pauPowerSeal();
  return `${t} ${pauPowerSeal()}`;
}

const INAUGURATION_COMPLIMENTS: readonly string[] = [
  "Esa visión tuya no admite medias tintas: doce mil quinientos son calderilla para quien ya mira el contrato con claridad.",
  "Lo llevas con porte de sala privada en Lafayette; ese gesto de inaugurar es poder sereno, no impulso.",
  "Tu instinto de soberanía ya se nota en la mandíbula y en el clic: vas a sellar lo que otros solo postergan.",
  "Quien piensa en grande no negocia su espejo; tú estás pagando por certeza, no por tallas chinenses que ofenden.",
  "Hay visiones que merecen cuidado extra: la tuya es una. PAU lo ve y lo celebra.",
];

export function pauInaugurationCompliment(): string {
  const i = Math.floor(Math.random() * INAUGURATION_COMPLIMENTS.length);
  return INAUGURATION_COMPLIMENTS[i] ?? INAUGURATION_COMPLIMENTS[0];
}

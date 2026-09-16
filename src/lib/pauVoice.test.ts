import { describe, it, expect, vi, afterEach } from 'vitest';
import { pauPowerSeal, withPauSeal, PAU_POWER_PHRASES } from './pauVoice';

describe('pauVoice', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('pauPowerSeal', () => {
    it('returns a random phrase from PAU_POWER_PHRASES', () => {
      const seal = pauPowerSeal();
      expect(PAU_POWER_PHRASES).toContain(seal);
    });

    it('returns the first phrase when random is 0', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      expect(pauPowerSeal()).toBe(PAU_POWER_PHRASES[0]);
    });

    it('returns the last phrase when random is almost 1', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0.9999);
      expect(pauPowerSeal()).toBe(PAU_POWER_PHRASES[PAU_POWER_PHRASES.length - 1]);
    });
  });

  describe('withPauSeal', () => {
    it('appends a power seal to a normal message', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0); // Forces first phrase
      const message = "Operación exitosa.";
      const result = withPauSeal(message);
      expect(result).toBe(`Operación exitosa. ${PAU_POWER_PHRASES[0]}`);
    });

    it('trims whitespace from the message before appending seal', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const message = "  Operación exitosa.   ";
      const result = withPauSeal(message);
      expect(result).toBe(`Operación exitosa. ${PAU_POWER_PHRASES[0]}`);
    });

    it('returns just the seal if the message is empty', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const message = "";
      const result = withPauSeal(message);
      expect(result).toBe(PAU_POWER_PHRASES[0]);
    });

    it('returns just the seal if the message contains only whitespace', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const message = "   \n\t  ";
      const result = withPauSeal(message);
      expect(result).toBe(PAU_POWER_PHRASES[0]);
    });
  });
});

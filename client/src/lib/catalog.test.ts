import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { getGarmentBySku, GARMENTS } from './catalog';

describe('getGarmentBySku', () => {
  let originalGarments: any[];

  beforeAll(() => {
    originalGarments = [...GARMENTS];
    // Clear the real array and inject the mock pilot data directly
    GARMENTS.length = 0;

    // Pilot mock data based on LAFAYETTE_INVENTORY
    GARMENTS.push(
      {
        id: "GL-001",
        ref: "GL-F-001",
        sku: "GL-F-001-SKU",
        name: "Robe de Soirée Soie",
        designer: "Lafayette Pilot",
        type: "robe",
        fabricKey: "silkElastic",
        fabricName: "Seda Elástica",
        price: 1200,
        tags: [],
        measurements: {
          shoulderCm: 40,
          chestCm: 90,
          waistCm: 70,
          hipCm: 95,
          lengthCm: 150
        },
        isHero: true,
        collection: "Pilot"
      } as any,
      {
        id: "GL-002",
        ref: "GL-M-002",
        sku: "GL-M-002-SKU",
        name: "Costume Laine Mérinos",
        designer: "Lafayette Pilot",
        type: "costume",
        fabricKey: "woolStandard",
        fabricName: "Laine",
        price: 1500,
        tags: [],
        measurements: {
          shoulderCm: 45,
          chestCm: 105,
          waistCm: 85,
          hipCm: 100,
          lengthCm: 75
        },
        isHero: false,
        collection: "Pilot"
      } as any
    );
  });

  afterAll(() => {
    // Restore the original array to avoid bleeding side effects
    GARMENTS.length = 0;
    GARMENTS.push(...originalGarments);
  });

  it('should return a garment when a valid exact sku is provided', () => {
    const garment = getGarmentBySku('GL-F-001-SKU');
    expect(garment).toBeDefined();
    expect(garment?.id).toBe('GL-001');
  });

  it('should return a garment when a valid exact ref is provided', () => {
    const garment = getGarmentBySku('GL-M-002');
    expect(garment).toBeDefined();
    expect(garment?.id).toBe('GL-002');
  });

  it('should handle whitespace trimming correctly', () => {
    const garmentSkuWithSpace = getGarmentBySku('  GL-F-001-SKU  ');
    expect(garmentSkuWithSpace).toBeDefined();
    expect(garmentSkuWithSpace?.id).toBe('GL-001');

    const garmentRefWithSpace = getGarmentBySku('GL-M-002 ');
    expect(garmentRefWithSpace).toBeDefined();
    expect(garmentRefWithSpace?.id).toBe('GL-002');
  });

  it('should return undefined for a non-existent sku', () => {
    const garment = getGarmentBySku('non-existent-sku');
    expect(garment).toBeUndefined();
  });

  it('should safely handle empty strings', () => {
    expect(getGarmentBySku('')).toBeUndefined();
    expect(getGarmentBySku('   ')).toBeUndefined();
  });

  it('should safely handle null inputs', () => {
    // @ts-expect-error testing invalid input
    expect(getGarmentBySku(null)).toBeUndefined();
  });

  it('should safely handle undefined inputs', () => {
    expect(getGarmentBySku(undefined)).toBeUndefined();
  });
});

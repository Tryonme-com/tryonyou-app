import { describe, it, expect } from 'vitest';
import { computeElasticityRatio, NormalizedLandmark } from './fabricFitComparator';

describe('computeElasticityRatio', () => {
  const createLandmarks = (
    l11: NormalizedLandmark = { x: 0, y: 0 },
    l12: NormalizedLandmark = { x: 0, y: 0 },
    l23: NormalizedLandmark = { x: 0, y: 0 },
    l24: NormalizedLandmark = { x: 0, y: 0 }
  ): NormalizedLandmark[] => {
    const arr = new Array(25).fill({ x: 0, y: 0 });
    arr[11] = l11;
    arr[12] = l12;
    arr[23] = l23;
    arr[24] = l24;
    return arr;
  };

  it('should return 0.5 if landmarks is null', () => {
    expect(computeElasticityRatio(null as any)).toBe(0.5);
  });

  it('should return 0.5 if landmarks length < 25', () => {
    expect(computeElasticityRatio(new Array(24).fill({ x: 0, y: 0 }))).toBe(0.5);
  });

  it('should return the correct ratio for normal landmarks', () => {
    // Shoulder dist = dist({x:0,y:0}, {x:3,y:4}) = 5
    // Hip dist = dist({x:0,y:0}, {x:0,y:2}) = 2
    // Ratio = 5 / 2 = 2.5
    const landmarks = createLandmarks(
      { x: 0, y: 0 }, { x: 3, y: 4 },
      { x: 0, y: 0 }, { x: 0, y: 2 }
    );
    expect(computeElasticityRatio(landmarks)).toBe(2.5);
  });

  it('should handle zero hip distance using 1e-6', () => {
    // Shoulder dist = dist({x:0,y:0}, {x:2,y:0}) = 2
    // Hip dist = dist({x:1,y:1}, {x:1,y:1}) = 0
    // Ratio = 2 / 1e-6 = 2000000
    const landmarks = createLandmarks(
      { x: 0, y: 0 }, { x: 2, y: 0 },
      { x: 1, y: 1 }, { x: 1, y: 1 }
    );
    expect(computeElasticityRatio(landmarks)).toBe(2000000);
  });

  it('should handle zero shoulder distance', () => {
    // Shoulder dist = dist({x:0,y:0}, {x:0,y:0}) = 0
    // Hip dist = dist({x:0,y:0}, {x:0,y:2}) = 2
    // Ratio = 0 / 2 = 0
    const landmarks = createLandmarks(
      { x: 0, y: 0 }, { x: 0, y: 0 },
      { x: 0, y: 0 }, { x: 0, y: 2 }
    );
    expect(computeElasticityRatio(landmarks)).toBe(0);
  });
});

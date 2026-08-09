import { describe, it, expect } from 'vitest';
import { computeElasticityRatio, NormalizedLandmark } from './fabricFitComparator';

describe('computeElasticityRatio', () => {
  const createMockLandmarks = (): NormalizedLandmark[] => {
    const landmarks = new Array(25).fill({ x: 0, y: 0 });
    return landmarks;
  };

  it('returns 0.5 when landmarks is null or undefined', () => {
    // @ts-expect-error testing invalid input
    expect(computeElasticityRatio(null)).toBe(0.5);
    // @ts-expect-error testing invalid input
    expect(computeElasticityRatio(undefined)).toBe(0.5);
  });

  it('returns 0.5 when landmarks array length is less than 25', () => {
    const shortLandmarks = new Array(24).fill({ x: 0, y: 0 });
    expect(computeElasticityRatio(shortLandmarks)).toBe(0.5);
  });

  it('calculates the elasticity ratio correctly for valid landmarks', () => {
    const landmarks = createMockLandmarks();
    // Shoulder (11, 12)
    landmarks[11] = { x: 0, y: 0 };
    landmarks[12] = { x: 4, y: 3 }; // dist2 = 5
    // Hip (23, 24)
    landmarks[23] = { x: 0, y: 0 };
    landmarks[24] = { x: 2, y: 0 }; // dist2 = 2
    // Expected ratio: 5 / 2 = 2.5

    expect(computeElasticityRatio(landmarks)).toBe(2.5);
  });

  it('handles hip distance of 0 using the 1e-6 safeguard', () => {
    const landmarks = createMockLandmarks();
    // Shoulder (11, 12)
    landmarks[11] = { x: 0, y: 0 };
    landmarks[12] = { x: 4, y: 0 }; // dist2 = 4
    // Hip (23, 24) -> Both have same coordinates so dist2 = 0
    landmarks[23] = { x: 0, y: 0 };
    landmarks[24] = { x: 0, y: 0 };
    // Expected ratio: 4 / 1e-6 = 4000000

    expect(computeElasticityRatio(landmarks)).toBe(4000000);
  });
});

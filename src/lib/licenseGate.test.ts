import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { isSovereigntyLicenseActive } from './licenseGate';

describe('isSovereigntyLicenseActive', () => {
  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('returns true for "true", "1", "yes", "on" ignoring case and whitespace', () => {
    vi.stubEnv('VITE_LICENSE_PAID', 'true');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', 'True ');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', '1');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', ' yes ');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', 'ON');
    expect(isSovereigntyLicenseActive()).toBe(true);
  });

  it('returns false for empty string', () => {
    vi.stubEnv('VITE_LICENSE_PAID', '');
    expect(isSovereigntyLicenseActive()).toBe(false);
  });

  it('returns false when undefined', () => {
    vi.stubEnv('VITE_LICENSE_PAID', undefined as any);
    expect(isSovereigntyLicenseActive()).toBe(false);
  });

  it('returns false for other truthy but invalid values', () => {
    vi.stubEnv('VITE_LICENSE_PAID', 'false');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', '0');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', 'no');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', 'random');
    expect(isSovereigntyLicenseActive()).toBe(false);
  });
});

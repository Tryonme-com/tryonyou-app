import { describe, it, expect, vi, afterEach } from 'vitest';
import { isSovereigntyLicenseActive } from './licenseGate';

describe('isSovereigntyLicenseActive', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('returns true for truthy values', () => {
    vi.stubEnv('VITE_LICENSE_PAID', 'true');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', '1');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', 'yes');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', 'on');
    expect(isSovereigntyLicenseActive()).toBe(true);
  });

  it('returns false for falsy or invalid values', () => {
    vi.stubEnv('VITE_LICENSE_PAID', '');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', 'false');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', '0');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', 'no');
    expect(isSovereigntyLicenseActive()).toBe(false);

    vi.stubEnv('VITE_LICENSE_PAID', 'random_string');
    expect(isSovereigntyLicenseActive()).toBe(false);
  });

  it('returns false when env is undefined', () => {
    const original = process.env.VITE_LICENSE_PAID;
    delete process.env.VITE_LICENSE_PAID;
    expect(isSovereigntyLicenseActive()).toBe(false);
    process.env.VITE_LICENSE_PAID = original;
  });

  it('handles case insensitivity and whitespace', () => {
    vi.stubEnv('VITE_LICENSE_PAID', ' TRUE ');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', 'Yes');
    expect(isSovereigntyLicenseActive()).toBe(true);

    vi.stubEnv('VITE_LICENSE_PAID', ' ON\n');
    expect(isSovereigntyLicenseActive()).toBe(true);
  });
});

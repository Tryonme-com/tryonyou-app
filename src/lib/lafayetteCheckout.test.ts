import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { getLafayetteStripeCheckoutUrl } from './lafayetteCheckout';

describe('getLafayetteStripeCheckoutUrl', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_LAFAYETTE_STRIPE_CHECKOUT_URL', '');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_4_5M', '');
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', '');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', '');
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('should return VITE_LAFAYETTE_STRIPE_CHECKOUT_URL when it is present', () => {
    vi.stubEnv('VITE_LAFAYETTE_STRIPE_CHECKOUT_URL', 'https://lafayette.example.com');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_4_5M', 'https://4_5m.example.com');
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', 'https://checkout.example.com');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', 'https://98k.example.com');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://lafayette.example.com');
  });

  it('should fallback to VITE_STRIPE_LINK_SOVEREIGNTY_4_5M if lafayette URL is missing', () => {
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_4_5M', 'https://4_5m.example.com');
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', 'https://checkout.example.com');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', 'https://98k.example.com');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://4_5m.example.com');
  });

  it('should fallback to VITE_STRIPE_CHECKOUT_URL if higher priority URLs are missing', () => {
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', 'https://checkout.example.com');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', 'https://98k.example.com');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://checkout.example.com');
  });

  it('should fallback to VITE_STRIPE_LINK_SOVEREIGNTY_98K if others are missing', () => {
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', 'https://98k.example.com');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://98k.example.com');
  });

  it('should ignore empty strings and whitespace strings', () => {
    vi.stubEnv('VITE_LAFAYETTE_STRIPE_CHECKOUT_URL', '   ');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_4_5M', '');
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', ' \n ');
    vi.stubEnv('VITE_STRIPE_LINK_SOVEREIGNTY_98K', 'https://98k.example.com');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://98k.example.com');
  });

  it('should trim the selected URL', () => {
    vi.stubEnv('VITE_STRIPE_CHECKOUT_URL', '  https://checkout.example.com  ');
    expect(getLafayetteStripeCheckoutUrl()).toBe('https://checkout.example.com');
  });

  it('should return empty string if no URLs are present', () => {
    expect(getLafayetteStripeCheckoutUrl()).toBe('');
  });
});

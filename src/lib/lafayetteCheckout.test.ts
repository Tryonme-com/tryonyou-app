import { describe, it, expect } from 'vitest';
import { getLafayetteStripeCheckoutUrl } from './lafayetteCheckout';

describe('getLafayetteStripeCheckoutUrl', () => {
  it('returns VITE_LAFAYETTE_STRIPE_CHECKOUT_URL if it exists', () => {
    const env = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: 'https://lafayette.example.com',
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: 'https://4_5m.example.com',
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.example.com',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.example.com',
    };
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('https://lafayette.example.com');
  });

  it('falls back to VITE_STRIPE_LINK_SOVEREIGNTY_4_5M if the first is missing', () => {
    const env = {
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: 'https://4_5m.example.com',
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.example.com',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.example.com',
    };
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('https://4_5m.example.com');
  });

  it('falls back to VITE_STRIPE_CHECKOUT_URL', () => {
    const env = {
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.example.com',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.example.com',
    };
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('https://checkout.example.com');
  });

  it('falls back to VITE_STRIPE_LINK_SOVEREIGNTY_98K', () => {
    const env = {
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.example.com',
    };
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('https://98k.example.com');
  });

  it('skips empty or whitespace-only candidates', () => {
    const env = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: '   ',
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: '',
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.example.com',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.example.com',
    };
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('https://checkout.example.com');
  });

  it('returns an empty string if no valid candidates exist', () => {
    const env = {};
    expect(getLafayetteStripeCheckoutUrl(env)).toBe('');
  });
});

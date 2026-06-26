import { test, describe } from 'node:test';
import assert from 'node:assert';
import { getLafayetteStripeCheckoutUrl } from './lafayetteCheckout.ts';

describe('getLafayetteStripeCheckoutUrl', () => {
  test('should return empty string if no environment variables are set', () => {
    const env = {} as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), '');
  });

  test('should return VITE_LAFAYETTE_STRIPE_CHECKOUT_URL if it is the only one set', () => {
    const env = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: 'https://lafayette.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://lafayette.url');
  });

  test('should prioritize VITE_LAFAYETTE_STRIPE_CHECKOUT_URL over others', () => {
    const env = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: 'https://lafayette.url',
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: 'https://4.5m.url',
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.url',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://lafayette.url');
  });

  test('should return VITE_STRIPE_LINK_SOVEREIGNTY_4_5M if VITE_LAFAYETTE_STRIPE_CHECKOUT_URL is missing', () => {
    const env = {
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: 'https://4.5m.url',
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.url',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://4.5m.url');
  });

  test('should return VITE_STRIPE_CHECKOUT_URL if first two are missing', () => {
    const env = {
      VITE_STRIPE_CHECKOUT_URL: 'https://checkout.url',
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://checkout.url');
  });

  test('should return VITE_STRIPE_LINK_SOVEREIGNTY_98K if others are missing', () => {
    const env = {
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: 'https://98k.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://98k.url');
  });

  test('should trim environment variable values', () => {
    const env = {
      VITE_STRIPE_CHECKOUT_URL: '  https://trimmed.url  '
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://trimmed.url');
  });

  test('should skip empty or whitespace-only values', () => {
    const env = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: '   ',
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: '',
      VITE_STRIPE_CHECKOUT_URL: 'https://valid.url'
    } as any;
    assert.strictEqual(getLafayetteStripeCheckoutUrl(env), 'https://valid.url');
  });
});

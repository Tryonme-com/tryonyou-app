import { describe, it, expect } from "vitest";
import { getLafayetteStripeCheckoutUrl } from "./lafayetteCheckout";

describe("getLafayetteStripeCheckoutUrl", () => {
  it("returns VITE_LAFAYETTE_STRIPE_CHECKOUT_URL if it exists", () => {
    const mockEnv = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: "https://lafayette.example.com",
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: "https://sov45m.example.com",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://lafayette.example.com");
  });

  it("returns VITE_STRIPE_LINK_SOVEREIGNTY_4_5M if VITE_LAFAYETTE_STRIPE_CHECKOUT_URL is missing", () => {
    const mockEnv = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: undefined,
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: "https://sov45m.example.com",
      VITE_STRIPE_CHECKOUT_URL: "https://checkout.example.com",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://sov45m.example.com");
  });

  it("returns VITE_STRIPE_CHECKOUT_URL if the first two are missing", () => {
    const mockEnv = {
      VITE_STRIPE_CHECKOUT_URL: "https://checkout.example.com",
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: "https://sov98k.example.com",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://checkout.example.com");
  });

  it("returns VITE_STRIPE_LINK_SOVEREIGNTY_98K if it is the only one present", () => {
    const mockEnv = {
      VITE_STRIPE_LINK_SOVEREIGNTY_98K: "https://sov98k.example.com",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://sov98k.example.com");
  });

  it("returns an empty string if no valid candidate is found", () => {
    const mockEnv = {};
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("");
  });

  it("ignores whitespace-only strings and moves to the next candidate", () => {
    const mockEnv = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: "   ",
      VITE_STRIPE_LINK_SOVEREIGNTY_4_5M: "https://sov45m.example.com",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://sov45m.example.com");
  });

  it("trims whitespace from the returned string", () => {
    const mockEnv = {
      VITE_LAFAYETTE_STRIPE_CHECKOUT_URL: "  https://lafayette.example.com  ",
    };
    expect(getLafayetteStripeCheckoutUrl(mockEnv)).toBe("https://lafayette.example.com");
  });
});

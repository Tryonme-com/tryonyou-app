import { useState } from "react";
import { PaymentElement, useStripe, useElements } from "@stripe/react-stripe-js";

interface CheckoutFormProps {
  returnUrl: string;
}

/**
 * Renders the Stripe PaymentElement and handles payment confirmation.
 *
 * Card data is tokenized entirely inside Stripe's iframe — raw card numbers
 * never reach this server.
 */
export default function CheckoutForm({ returnUrl }: CheckoutFormProps) {
  const stripe = useStripe();
  const elements = useElements();

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: returnUrl },
    });

    // confirmPayment only returns here if there is an immediate error.
    // Otherwise the customer is redirected to returnUrl.
    if (error) {
      setErrorMessage(error.message ?? "Une erreur est survenue.");
    }

    setIsLoading(false);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <PaymentElement />

      {errorMessage && (
        <p className="text-sm text-red-400 border border-red-400/30 rounded px-3 py-2">
          {errorMessage}
        </p>
      )}

      <button
        type="submit"
        disabled={!stripe || isLoading}
        className="w-full py-3 px-6 rounded font-medium tracking-widest uppercase text-sm
                   bg-[var(--color-or)] text-[#0A0807] hover:opacity-90
                   disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
      >
        {isLoading ? "Traitement…" : "Confirmer le paiement"}
      </button>
    </form>
  );
}

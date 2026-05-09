/**
 * Maison Couture Nocturne — Contact / lead capture.
 * POSTs to /api/v1/leads (Flask SQLite endpoint).
 */
import { useState } from "react";
import { toast } from "sonner";

type LeadStatus = "idle" | "submitting" | "ok" | "error";

export default function Contact() {
  const [status, setStatus] = useState<LeadStatus>("idle");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const payload = {
      full_name: String(fd.get("full_name") || "").trim(),
      email: String(fd.get("email") || "").trim(),
      company: String(fd.get("company") || "").trim(),
      role: String(fd.get("role") || "").trim(),
      market: String(fd.get("market") || "").trim(),
      challenge: String(fd.get("challenge") || "").trim(),
      consent: fd.get("consent") === "on",
      source: "tryonyou.app",
      submitted_at: new Date().toISOString(),
    };
    if (!payload.full_name || !payload.email || !payload.company || !payload.consent) {
      toast.error("Merci de remplir les champs obligatoires.");
      return;
    }
    setStatus("submitting");
    try {
      const resp = await fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error("network");
      setStatus("ok");
      toast.success("Demande reçue. Nous vous recontactons sous 48 h.");
      (e.target as HTMLFormElement).reset();
    } catch {
      setStatus("error");
      toast.error("Erreur d'envoi. Réessayez ou écrivez à contact@tryonyou.app.");
    }
  };

  return (
    <section id="contact" className="relative py-24 md:py-36 bg-[var(--color-graphite)]">
      <div className="container">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          <div className="lg:col-span-5 reveal-up">
            <div className="roman mb-6">VI</div>
            <span className="eyebrow mb-5 inline-flex">Contact</span>
            <h2 className="display-l mb-8">
              Parlons de votre
              <br />
              <span className="accent-italic">prochain pilote.</span>
            </h2>
            <p className="text-[17px] leading-[1.75] text-[var(--color-ivoire)]/80 mb-10 max-w-[42ch]">
              Une démonstration live, vos catégories sensibles analysées, une
              estimation d'impact dédiée à votre maison. Réponse en 48 heures
              ouvrées par notre équipe parisienne.
            </p>

            <div className="space-y-5">
              <div>
                <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)] mb-1">
                  Direction commerciale
                </div>
                <a href="mailto:contact@tryonyou.app" className="font-display italic text-[var(--color-or)] text-[22px] hover:text-[var(--color-or-pale)] transition-colors">
                  contact@tryonyou.app
                </a>
              </div>
              <div>
                <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)] mb-1">
                  Siège
                </div>
                <div className="text-[16px] text-[var(--color-ivoire)]/85">
                  Paris&nbsp;·&nbsp;France
                </div>
              </div>
              <div>
                <div className="text-[10px] tracking-[0.24em] uppercase text-[var(--color-fog)] mb-1">
                  SIREN
                </div>
                <div className="text-[16px] text-[var(--color-ivoire)]/85 tracking-wider">
                  943 610 196
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-6 lg:col-start-7 reveal-up" data-delay="180">
            <form
              onSubmit={handleSubmit}
              className="border border-[rgba(201,168,76,0.3)] p-8 md:p-12 bg-[rgba(10,8,7,0.6)] backdrop-blur-sm space-y-7"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="field">
                  <label htmlFor="full_name">Nom complet *</label>
                  <input id="full_name" name="full_name" type="text" required autoComplete="name" />
                </div>
                <div className="field">
                  <label htmlFor="email">Email professionnel *</label>
                  <input id="email" name="email" type="email" required autoComplete="email" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="field">
                  <label htmlFor="company">Maison / Enseigne *</label>
                  <input id="company" name="company" type="text" required />
                </div>
                <div className="field">
                  <label htmlFor="role">Fonction</label>
                  <input id="role" name="role" type="text" placeholder="Direction Digital, Retail, E-commerce…" />
                </div>
              </div>

              <div className="field">
                <label htmlFor="market">Marché principal</label>
                <select id="market" name="market" defaultValue="">
                  <option value="" disabled>Sélectionner…</option>
                  <option value="France">France</option>
                  <option value="Europe">Europe</option>
                  <option value="Amérique du Nord">Amérique du Nord</option>
                  <option value="Asie">Asie</option>
                  <option value="Moyen-Orient">Moyen-Orient</option>
                  <option value="Global">Global</option>
                </select>
              </div>

              <div className="field">
                <label htmlFor="challenge">Votre enjeu principal</label>
                <textarea
                  id="challenge"
                  name="challenge"
                  rows={4}
                  placeholder="Catégorie sensible, volume mensuel, objectifs de réduction des retours…"
                />
              </div>

              <label className="flex items-start gap-3 text-[13px] text-[var(--color-ivoire)]/75 leading-snug">
                <input
                  type="checkbox"
                  name="consent"
                  required
                  className="mt-1 accent-[var(--color-or)] w-4 h-4 cursor-pointer"
                />
                <span>
                  J'accepte d'être recontacté(e) par TRYONYOU concernant ma demande.
                  Vos données sont traitées conformément au RGPD et ne sont jamais
                  partagées. *
                </span>
              </label>

              <button
                type="submit"
                disabled={status === "submitting"}
                className="btn-or w-full justify-center disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {status === "submitting" ? "Envoi en cours…" : "Envoyer ma demande"}
                {status !== "submitting" && <span aria-hidden>→</span>}
              </button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}

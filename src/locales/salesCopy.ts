export type AppLocale = "fr" | "en" | "es";

export const SUPPORTED_LOCALES: readonly AppLocale[] = ["fr", "en", "es"];

export type SalesCopy = {
  localeLabel: string;
  badge: string;
  heroTitle: string;
  heroLead: string;
  heroEmailPlaceholder: string;
  heroEmailPrompt: string;
  heroCta: string;
  housePhrases: readonly string[];
  inaugurationCta: string;
  inaugurationTitle: string;
  inaugurationAriaLabel: string;
  lafayetteCta: string;
  checkoutHint: string;
  betaCta: string;
  packStarterTitle: string;
  packStarterBody: string;
  packMaisonTitle: string;
  packMaisonBody: string;
  videoOneTitle: string;
  videoOneBody: string;
  videoTwoTitle: string;
  videoTwoBody: string;
  heroSlotError: string;
  heroSlotReserved: string;
  heroSlotReceived: string;
  bunkerOffline: string;
  inaugurationMissingCheckout: string;
  lafayetteMissingCheckout: string;
  ofrendaBalmain: string;
  ofrendaReserve: string;
  ofrendaCombo: string;
  ofrendaSave: string;
  ofrendaShare: string;
  ofrendaSelection: string;
  overlayReserve: string;
  overlayCombos: string;
  overlayMuseum: string;
  overlayShare: string;
  betaPromptEmail: string;
  betaApiError: string;
  betaWaitlistStored: string;
  betaWebhookStatusOk: string;
  betaWebhookStatusFail: string;
  betaWebhookStatusTemplate: string;
  bridgeConfigured: string;
  bridgeLimited: string;
  perfectSelectionFallback: string;
  manifestoTag: string;
  manifestoTitle: string;
  manifestoBody: string;
  manifestoAccumulation: string;
  manifestoColor: string;
  manifestoIdentity: string;
  manifestoCta: string;
  manifestoSlogan: string;
  manifestoHashtags: string;
  manifestoLafayette: string;
  pauGuideGreeting: string;
  pauGuideScan: string;
  pauGuideSnap: string;
  pauGuideNext: string;
};

export const SALES_COPY: Record<AppLocale, SalesCopy> = {
  fr: {
    localeLabel: "Langue de la Maison",
    badge: "TRYONYOU · MAISON PAU · DIVINEO",
    heroTitle: "P.A.U. du premier au dernier instant, prêt à vendre dès maintenant.",
    heroLead:
      "Miroir digital souverain en euro, sans tailles classiques. Vous voyez l'ajustage avant de payer.",
    heroEmailPlaceholder: "Votre email pour commencer aujourd'hui",
    heroEmailPrompt: "Email pour commencer aujourd'hui:",
    heroCta: "Essayer maintenant (5 créneaux aujourd'hui)",
    housePhrases: [
      "Aucune taille classique, uniquement la certitude souveraine.",
      "Monnaie officielle: EUR. Ventes prêtes pour Lafayette et Marais.",
    ],
    inaugurationCta: "PAYER — INAUGURATION",
    inaugurationTitle: "PAU — inauguration souveraine LIVE en EUR.",
    inaugurationAriaLabel: "PAU — payer inauguration en euro via Stripe",
    lafayetteCta: "Contrat Lafayette (Stripe)",
    checkoutHint: " · checkout Divineo V11 → abvetos.com",
    betaCta: "Rejoindre la bêta",
    packStarterTitle: "Pack Inauguration",
    packStarterBody: "Activation commerciale immédiate pour le lancement.",
    packMaisonTitle: "Pack Maison Lafayette",
    packMaisonBody: "Déploiement premium avec orchestration P.A.U. complète.",
    videoOneTitle: "Intro commerciale PAU",
    videoOneBody: "Vidéo d'ouverture prête pour acquisition et social ads.",
    videoTwoTitle: "Offre souveraine EUR",
    videoTwoBody: "Vidéo de closing prête pour vente directe en euro.",
    heroSlotError:
      "Impossible de réserver votre créneau maintenant. Réessayez dans quelques minutes.",
    heroSlotReserved: "Créneau confirmé. Notre équipe vous contacte aujourd'hui.",
    heroSlotReceived: "Demande reçue. Le bunker confirme sous peu.",
    bunkerOffline: "Connexion bunker API indisponible.",
    inaugurationMissingCheckout:
      "Liquidité: configurez VITE_INAUGURATION_STRIPE_CHECKOUT_URL (Payment Link LIVE) sur Vercel ou .env.",
    lafayetteMissingCheckout:
      "Contrat Lafayette: configurez VITE_LAFAYETTE_STRIPE_CHECKOUT_URL (Stripe Payment Link LIVE) sur Vercel ou .env.",
    ofrendaBalmain:
      "Ligne Balmain — Espejo Digital notifié; poursuite sous protocole Zero-Size.",
    ofrendaReserve: "QR cabine VIP — Lafayette, essai en courtoisie Divineo.",
    ofrendaCombo: "Lignes alternatives chargées — composition Zero-Size.",
    ofrendaSave: "Silhouette enregistrée sous protocole chiffré (aucune taille exposée).",
    ofrendaShare: "Partage généré — métadonnées d’ajustage neutralisées.",
    ofrendaSelection: "Paiement carte — Non-Stop (sélection parfaite)",
    overlayReserve: "Réserver en cabine",
    overlayCombos: "Voir les combinaisons",
    overlayMuseum: "Sac Museum",
    overlayShare: "Partager le look VIP",
    betaPromptEmail: "Email (optionnel) pour la liste bêta:",
    betaApiError: "Liste bêta: erreur API (vérifiez la console).",
    betaWaitlistStored:
      "Inscription validée — Make + waitlist (leads_empire/waitlist.json ou /tmp sur Vercel).",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "non configuré / erreur",
    betaWebhookStatusTemplate: "Webhook Make: {{status}}. Persistance limitée en serverless.",
    bridgeConfigured:
      "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
    bridgeLimited:
      "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
    perfectSelectionFallback:
      "Parcours enregistré — les ponts marchands seront actifs dès configuration serveur (Zero-Size).",
    manifestoTag: "MANIFESTE · PARIS 2026",
    manifestoTitle: "LE LUXE ET LE NON-SENS",
    manifestoBody:
      "Parlons de luxe. Mais du vrai luxe : une boutique divine sans cintres. Un claquement de doigts et vous essayez la dernière collection de vos créateurs préférés ; que la vente arrive directement à votre hôtel et que vous ne vous concentriez que sur une chose : promener ce look et ce sac chez Lafayette.",
    manifestoAccumulation:
      "L'accumulation n'est ni belle ni élégante. Tu finis par être la pire de la boutique avec tes trois tailles emmêlées dans un clapier de 30 m². C'est absurde. Donne ces fringues à ceux qui en ont besoin ; si tu as le cash, achète-t'en une, porte-la avec panache et quand tu en as marre, passe à la suivante.",
    manifestoColor:
      "Pourquoi ne pourrais-tu pas te sentir « rouge » un jour ? Mon invention est pour nous identifier, pour nous exprimer plus artistiquement et pour que nous soyons PLUS LIBRES.",
    manifestoIdentity:
      "Toi qui peux te le payer, cherche-toi et identifie-toi. Marque à nouveau la tendance en tant que citoyenne de Paris, la capitale de la mode. Rends-toi divine, montre-toi, ne laisse pas les autres te le raconter : vis-le.",
    manifestoCta: "QUE PARIS SE ROMPE AVEC TA COULEUR !",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #Paris2026 #FashionTech",
    manifestoLafayette:
      "L'innovation est désormais une réalité aux Galeries Lafayette avec notre miroir « Divineo ».",
    pauGuideGreeting:
      "Bonjour ! Je suis P.A.U., votre guide personnel. Prête pour une expérience unique ?",
    pauGuideScan:
      "Regardez la caméra… je mesure votre silhouette avec précision biométrique.",
    pauGuideSnap: "✨ Claquement ! Voici votre look parfait.",
    pauGuideNext: "Un autre claquement… et un nouveau look apparaît !",
  },
  en: {
    localeLabel: "House language",
    badge: "TRYONYOU · MAISON PAU · DIVINEO",
    heroTitle: "P.A.U. from start to finish, ready to sell right now.",
    heroLead:
      "Sovereign digital mirror in euro, with no classic sizing. See fit certainty before payment.",
    heroEmailPlaceholder: "Your email to start today",
    heroEmailPrompt: "Email to start today:",
    heroCta: "Try now (5 slots today)",
    housePhrases: [
      "No classic sizes, only sovereign certainty.",
      "Official currency: EUR. Sales ready for Lafayette and Marais.",
    ],
    inaugurationCta: "PAY — INAUGURATION",
    inaugurationTitle: "PAU — sovereign LIVE inauguration in EUR.",
    inaugurationAriaLabel: "PAU — pay inauguration in euro via Stripe",
    lafayetteCta: "Lafayette contract (Stripe)",
    checkoutHint: " · Divineo V11 checkout → abvetos.com",
    betaCta: "Join beta",
    packStarterTitle: "Inauguration Pack",
    packStarterBody: "Immediate commercial activation for launch.",
    packMaisonTitle: "Lafayette Maison Pack",
    packMaisonBody: "Premium deployment with full P.A.U. orchestration.",
    videoOneTitle: "PAU commercial intro",
    videoOneBody: "Opening video ready for acquisition and social ads.",
    videoTwoTitle: "EUR sovereign offer",
    videoTwoBody: "Closing video ready for direct euro sales.",
    heroSlotError: "We could not reserve your slot now. Try again in a few minutes.",
    heroSlotReserved: "Slot confirmed. Our team will contact you today.",
    heroSlotReceived: "Request received. The bunker will confirm shortly.",
    bunkerOffline: "Bunker API connection unavailable.",
    inaugurationMissingCheckout:
      "Liquidity: configure VITE_INAUGURATION_STRIPE_CHECKOUT_URL (LIVE Payment Link) in Vercel or .env.",
    lafayetteMissingCheckout:
      "Lafayette contract: configure VITE_LAFAYETTE_STRIPE_CHECKOUT_URL (LIVE Stripe Payment Link) in Vercel or .env.",
    ofrendaBalmain:
      "Balmain line — Digital mirror notified; Zero-Size protocol continues.",
    ofrendaReserve: "VIP cabin QR — Lafayette fitting in Divineo courtesy mode.",
    ofrendaCombo: "Alternative lines loaded — Zero-Size composition.",
    ofrendaSave: "Silhouette saved under encrypted protocol (no exposed size).",
    ofrendaShare: "Share generated — fitting metadata neutralized.",
    ofrendaSelection: "Card payment — Non-Stop (perfect selection)",
    overlayReserve: "Reserve fitting suite",
    overlayCombos: "View combinations",
    overlayMuseum: "Sac Museum",
    overlayShare: "Share VIP look",
    betaPromptEmail: "Email (optional) for beta waitlist:",
    betaApiError: "Beta waitlist: API error (check console).",
    betaWaitlistStored:
      "Signed up — Make + waitlist (leads_empire/waitlist.json or /tmp on Vercel).",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "not configured / failed",
    betaWebhookStatusTemplate: "Make webhook: {{status}}. Persistence is limited in serverless.",
    bridgeConfigured:
      "Journey saved — merchant bridges become active once server config is completed (Zero-Size).",
    bridgeLimited:
      "Journey saved — merchant bridges become active once server config is completed (Zero-Size).",
    perfectSelectionFallback:
      "Journey saved — merchant bridges become active once server config is completed (Zero-Size).",
    manifestoTag: "MANIFESTO · PARIS 2026",
    manifestoTitle: "LUXURY AND NONSENSE",
    manifestoBody:
      "Let's talk luxury. Real luxury: a divine boutique with no hangers. A snap of the fingers and you try on the latest collection from your favourite designers; the purchase arrives at your hotel and you focus on one thing only: walking that look and that bag at Lafayette.",
    manifestoAccumulation:
      "Accumulation is neither beautiful nor elegant. You end up being the worst in the boutique with three tangled sizes in a 30 m² hutch. It's absurd. Give those clothes to those who need them; if you have the cash, buy one, wear it with panache and when you're tired of it, move on.",
    manifestoColor:
      "Why couldn't you feel 'red' today? My invention is to identify ourselves, to express ourselves more artistically and to be MORE FREE.",
    manifestoIdentity:
      "You who can afford it: find yourself and identify yourself. Set the trend again as a citizen of Paris, the fashion capital. Make yourself divine, show yourself, don't let others tell you about it: LIVE IT.",
    manifestoCta: "LET PARIS BREAK WITH YOUR COLOUR!",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #Paris2026 #FashionTech",
    manifestoLafayette:
      "Innovation is now a reality at Galeries Lafayette with our 'Divineo' mirror.",
    pauGuideGreeting:
      "Hello! I'm P.A.U., your personal guide. Ready for a unique experience?",
    pauGuideScan:
      "Look at the camera… I'm measuring your silhouette with biometric precision.",
    pauGuideSnap: "✨ Snap! Here's your perfect look.",
    pauGuideNext: "Another snap… and a new look appears!",
  },
  es: {
    localeLabel: "Idioma de la casa",
    badge: "TRYONYOU · MAISON PAU · DIVINEO",
    heroTitle: "P.A.U. desde el principio al final, listo para vender desde ya.",
    heroLead:
      "Espejo digital soberano en euro, sin tallas clásicas. Ves el ajuste antes de pagar.",
    heroEmailPlaceholder: "Tu email para empezar hoy",
    heroEmailPrompt: "Email para empezar hoy:",
    heroCta: "Pruébatela YA (5 slots hoy)",
    housePhrases: [
      "Sin tallas clásicas, solo certeza soberana.",
      "Moneda oficial: EUR. Venta lista para Lafayette y Marais.",
    ],
    inaugurationCta: "PAGAR — INAUGURACIÓN",
    inaugurationTitle: "PAU — inauguración soberana LIVE en EUR.",
    inaugurationAriaLabel: "PAU — pagar inauguración en euro vía Stripe",
    lafayetteCta: "Contrato Lafayette (Stripe)",
    checkoutHint: " · checkout Divineo V11 → abvetos.com",
    betaCta: "Únete a la beta",
    packStarterTitle: "Pack Inauguración",
    packStarterBody: "Activación comercial inmediata para lanzamiento.",
    packMaisonTitle: "Pack Maison Lafayette",
    packMaisonBody: "Despliegue premium con orquestación P.A.U. completa.",
    videoOneTitle: "Intro comercial PAU",
    videoOneBody: "Vídeo de apertura listo para adquisición y social ads.",
    videoTwoTitle: "Oferta soberana EUR",
    videoTwoBody: "Vídeo de cierre listo para venta directa en euro.",
    heroSlotError: "No hemos podido reservar tu slot ahora. Prueba en unos minutos.",
    heroSlotReserved: "Slot confirmado. Nuestro equipo te contacta hoy.",
    heroSlotReceived: "Solicitud recibida. El bunker confirma en breve.",
    bunkerOffline: "Conexión con bunker API no disponible.",
    inaugurationMissingCheckout:
      "Liquidez: configura VITE_INAUGURATION_STRIPE_CHECKOUT_URL (Payment Link LIVE) en Vercel o .env.",
    lafayetteMissingCheckout:
      "Contrato Lafayette: define VITE_LAFAYETTE_STRIPE_CHECKOUT_URL (Stripe Payment Link LIVE) en Vercel o .env.",
    ofrendaBalmain: "Línea Balmain — Espejo Digital notificado; continuidad Zero-Size.",
    ofrendaReserve: "QR cabina VIP — Lafayette, prueba en cortesía Divineo.",
    ofrendaCombo: "Líneas alternativas cargadas — composición Zero-Size.",
    ofrendaSave: "Silueta guardada bajo protocolo cifrado (sin talla expuesta).",
    ofrendaShare: "Compartido generado — metadatos de ajuste neutralizados.",
    ofrendaSelection: "Pago tarjeta — Non-Stop (selección perfecta)",
    overlayReserve: "Reservar en probador",
    overlayCombos: "Ver combinaciones",
    overlayMuseum: "Sac Museum",
    overlayShare: "Compartir look VIP",
    betaPromptEmail: "Email (opcional) para la lista beta:",
    betaApiError: "Lista beta: error de API (revisa consola).",
    betaWaitlistStored:
      "Inscrito — Make + waitlist (leads_empire/waitlist.json o /tmp en Vercel).",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "no configurado / fallo",
    betaWebhookStatusTemplate: "Webhook Make: {{status}}. Persistencia limitada en serverless.",
    bridgeConfigured:
      "Recorrido registrado — los puentes de venta se activarán al completar configuración de servidor (Zero-Size).",
    bridgeLimited:
      "Recorrido registrado — los puentes de venta se activarán al completar configuración de servidor (Zero-Size).",
    perfectSelectionFallback:
      "Recorrido registrado — los puentes de venta se activarán al completar configuración de servidor (Zero-Size).",
    manifestoTag: "MANIFIESTO · PARÍS 2026",
    manifestoTitle: "EL LUJO Y EL SINSENTIDO",
    manifestoBody:
      "Hablemos de lujo. Pero del verdadero lujo: una boutique divina sin perchas. Un chasquido de dedos y te pruebas la última colección de tus creadores favoritos; que la venta llegue directamente a tu hotel y que solo te concentres en una cosa: pasear ese look y ese bolso en Lafayette.",
    manifestoAccumulation:
      "La acumulación no es bella ni elegante. Acabas siendo la peor de la boutique con tus tres tallas enredadas en un cuchitril de 30 m². Es absurdo. Da esa ropa a quien la necesite; si tienes el cash, cómprate una, llévala con garbo y cuando te canses, pasa a la siguiente.",
    manifestoColor:
      "¿Por qué no podrías sentirte « rojo » hoy? Mi invención es para identificarnos, para expresarnos más artísticamente y para que seamos MÁS LIBRES.",
    manifestoIdentity:
      "Tú, que puedes pagarlo: búscate e identifícate. Marca de nuevo la tendencia como ciudadana de la capital de la moda. Ponte divina, muéstrate y no dejes que otros te lo cuenten: VÍVELO.",
    manifestoCta: "¡QUE PARÍS SE ROMPA CON TU COLOR!",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #Paris2026 #FashionTech",
    manifestoLafayette:
      "La innovación es ya una realidad en las Galeries Lafayette con nuestro espejo « Divineo ».",
    pauGuideGreeting:
      "¡Hola! Soy P.A.U., tu guía personal. ¿Lista para una experiencia única?",
    pauGuideScan:
      "Mira a la cámara… estoy midiendo tu silueta con precisión biométrica.",
    pauGuideSnap: "✨ ¡Chasquido! Aquí está tu look perfecto.",
    pauGuideNext: "¡Otro chasquido… y aparece un nuevo look!",
  },
};

export function formatEurAmount(amount: number, locale: AppLocale): string {
  const localeTag = locale === "fr" ? "fr-FR" : locale === "en" ? "en-IE" : "es-ES";
  return new Intl.NumberFormat(localeTag, {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
  }).format(amount);
}

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
  demoFormSubmitting: string;
  demoFormSuccessTitle: string;
  demoFormSuccessBody: string;
  demoFormError: string;
  demoFormRetry: string;
  demoFormCatalogPlaceholder: string;
};

export const SALES_COPY: Record<AppLocale, SalesCopy> = {
  fr: {
    localeLabel: "Langue",
    badge: "TRYONYOU · ZERO-SIZE PROTOCOL",
    heroTitle: "L'essayage virtuel qui réduit les retours",
    heroLead:
      "TryOnYou crée un jumeau numérique de chaque client pour simuler l'ajustement réel des vêtements — avant l'achat.",
    heroEmailPlaceholder: "Votre email professionnel",
    heroEmailPrompt: "Votre email professionnel :",
    heroCta: "Demander une démo",
    housePhrases: [
      "Nous ne vendons pas des vêtements. Nous vendons la certitude du fit.",
      "Retailers, grands magasins et groupes mode : déploiement B2B, pas D2C.",
    ],
    inaugurationCta: "Demander une démo",
    inaugurationTitle: "Demander une démonstration enterprise TryOnYou",
    inaugurationAriaLabel: "Demander une démonstration enterprise TryOnYou",
    lafayetteCta: "Contacter l'équipe",
    checkoutHint: " · démonstration enterprise sur rendez-vous",
    betaCta: "Demander une démo",
    packStarterTitle: "Pilote retail",
    packStarterBody: "Validation rapide sur un périmètre restreint avec KPI de retour et conversion.",
    packMaisonTitle: "Déploiement enterprise",
    packMaisonBody: "Intégration omnicanale pour retailers et groupes mode multi-marques.",
    videoOneTitle: "Expérience d'essayage",
    videoOneBody: "Le client entre, se scanne et voit le résultat avant achat.",
    videoTwoTitle: "Impact business",
    videoTwoBody: "Le retailer réduit les retours, augmente la conversion et collecte un ROI mesurable.",
    heroSlotError: "Impossible d'envoyer la demande pour le moment.",
    heroSlotReserved: "Demande envoyée. Notre équipe vous contacte rapidement.",
    heroSlotReceived: "Demande reçue. Nous revenons vers vous rapidement.",
    bunkerOffline: "Service temporairement indisponible. Veuillez réessayer.",
    inaugurationMissingCheckout:
      "Lien indisponible. Utilisez le formulaire de démo pour contacter l'équipe commerciale.",
    lafayetteMissingCheckout:
      "Lien indisponible. Utilisez le formulaire de démo pour contacter l'équipe commerciale.",
    ofrendaBalmain:
      "Intérêt enregistré côté miroir digital sous protocole Zero-Size.",
    ofrendaReserve: "Demande d'essayage assisté enregistrée.",
    ofrendaCombo: "Simulation alternative chargée sous protocole Zero-Size.",
    ofrendaSave: "Silhouette enregistrée sous protocole chiffré.",
    ofrendaShare: "Partage généré avec métadonnées neutralisées.",
    ofrendaSelection: "Sélection parfaite prête.",
    overlayReserve: "Réserver",
    overlayCombos: "Voir variantes",
    overlayMuseum: "Sauvegarder",
    overlayShare: "Partager",
    betaPromptEmail: "Votre email professionnel (optionnel) :",
    betaApiError: "Erreur API lors de l'enregistrement.",
    betaWaitlistStored: "Demande enregistrée avec succès.",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "non configuré",
    betaWebhookStatusTemplate: "Statut webhook : {{status}}.",
    bridgeConfigured:
      "Parcours enregistré — activation commerciale côté serveur requise pour les ponts marchands.",
    bridgeLimited:
      "Parcours enregistré — activation commerciale côté serveur requise pour les ponts marchands.",
    perfectSelectionFallback:
      "Parcours enregistré — les liens de vente seront activés après configuration serveur.",
    manifestoTag: "VISION",
    manifestoTitle: "Le futur du fit n'est pas une taille, c'est une prédiction.",
    manifestoBody:
      "TryOnYou transforme l'essayage en infrastructure de décision pour le retail mode. Nous remplaçons l'incertitude par une simulation exploitable avant achat.",
    manifestoAccumulation:
      "Moins de friction, moins de retours, plus de confiance : la technologie doit retirer de la complexité, pas en ajouter.",
    manifestoColor:
      "Le fit devient mesurable, le choix devient plus rapide et l'expérience reste désirable.",
    manifestoIdentity:
      "Nous ne vendons pas une garde-robe. Nous donnons aux retailers la certitude nécessaire pour vendre mieux.",
    manifestoCta: "Le commerce mode mérite la certitude.",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #FashionTech #RetailAI",
    manifestoLafayette: "Pilotes en cours avec retailers européens.",
    pauGuideGreeting:
      "Bonjour, je suis P.A.U., votre assistant d'essayage IA.",
    pauGuideScan:
      "Je guide le client à travers le scan et la capture biométrique.",
    pauGuideSnap: "Je montre le rendu du vêtement en temps réel.",
    pauGuideNext: "Je l'aide à décider avec certitude avant achat.",
    demoFormSubmitting: "Envoi en cours…",
    demoFormSuccessTitle: "Merci.",
    demoFormSuccessBody: "Votre demande de démo a bien été envoyée. Notre équipe vous contacte rapidement.",
    demoFormError: "Impossible d'envoyer la demande pour le moment.",
    demoFormRetry: "Veuillez réessayer dans quelques instants.",
    demoFormCatalogPlaceholder: "Sélectionner une tranche",
  },
  en: {
    localeLabel: "Language",
    badge: "TRYONYOU · ZERO-SIZE PROTOCOL",
    heroTitle: "The virtual fitting room that reduces returns",
    heroLead:
      "TryOnYou creates a digital twin of each customer to simulate real garment fit — before purchase.",
    heroEmailPlaceholder: "Your professional email",
    heroEmailPrompt: "Your professional email:",
    heroCta: "Request Demo",
    housePhrases: [
      "We do not sell clothes. We sell fit certainty.",
      "Built for retailers, department stores and fashion groups.",
    ],
    inaugurationCta: "Request a demo",
    inaugurationTitle: "Request a TryOnYou enterprise demo",
    inaugurationAriaLabel: "Request a TryOnYou enterprise demo",
    lafayetteCta: "Contact sales",
    checkoutHint: " · enterprise demo by appointment",
    betaCta: "Request a demo",
    packStarterTitle: "Retail pilot",
    packStarterBody: "Fast validation on a focused scope with return and conversion KPIs.",
    packMaisonTitle: "Enterprise rollout",
    packMaisonBody: "Omnichannel integration for retailers and multi-brand fashion groups.",
    videoOneTitle: "Try-on experience",
    videoOneBody: "The customer scans and sees the result before purchase.",
    videoTwoTitle: "Business impact",
    videoTwoBody: "The retailer reduces returns, lifts conversion and gets measurable ROI.",
    heroSlotError: "We could not send the request right now.",
    heroSlotReserved: "Request sent. Our team will contact you shortly.",
    heroSlotReceived: "Request received. We will get back to you shortly.",
    bunkerOffline: "Service temporarily unavailable. Please try again.",
    inaugurationMissingCheckout:
      "Link unavailable. Please use the demo form to contact the sales team.",
    lafayetteMissingCheckout:
      "Link unavailable. Please use the demo form to contact the sales team.",
    ofrendaBalmain:
      "Interest logged in the digital mirror under Zero-Size protocol.",
    ofrendaReserve: "Assisted fitting request recorded.",
    ofrendaCombo: "Alternative simulation loaded under Zero-Size protocol.",
    ofrendaSave: "Silhouette saved under encrypted protocol.",
    ofrendaShare: "Share generated with neutralized metadata.",
    ofrendaSelection: "Perfect selection ready.",
    overlayReserve: "Reserve",
    overlayCombos: "View options",
    overlayMuseum: "Save",
    overlayShare: "Share",
    betaPromptEmail: "Your professional email (optional):",
    betaApiError: "API error while saving the request.",
    betaWaitlistStored: "Request saved successfully.",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "not configured",
    betaWebhookStatusTemplate: "Webhook status: {{status}}.",
    bridgeConfigured:
      "Journey saved — server activation is still required for merchant bridges.",
    bridgeLimited:
      "Journey saved — server activation is still required for merchant bridges.",
    perfectSelectionFallback:
      "Journey saved — sales links will be activated after server configuration.",
    manifestoTag: "VISION",
    manifestoTitle: "The future of fit is not a size. It is a prediction.",
    manifestoBody:
      "TryOnYou turns fitting into decision infrastructure for fashion retail. We replace uncertainty with a usable simulation before purchase.",
    manifestoAccumulation:
      "Less friction, fewer returns, more trust: technology should remove complexity, not add to it.",
    manifestoColor:
      "Fit becomes measurable, decision-making becomes faster and the experience remains desirable.",
    manifestoIdentity:
      "We do not sell a wardrobe. We give retailers the certainty they need to sell better.",
    manifestoCta: "Fashion commerce deserves certainty.",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #FashionTech #RetailAI",
    manifestoLafayette: "Pilots underway with European retailers.",
    pauGuideGreeting:
      "Hello, I'm P.A.U., your AI fitting assistant.",
    pauGuideScan:
      "I guide the customer through scan and biometric capture.",
    pauGuideSnap: "I show the garment result in real time.",
    pauGuideNext: "I help them decide with certainty before purchase.",
    demoFormSubmitting: "Sending…",
    demoFormSuccessTitle: "Thank you.",
    demoFormSuccessBody: "Your demo request has been sent. Our team will contact you shortly.",
    demoFormError: "We could not send the request right now.",
    demoFormRetry: "Please try again in a moment.",
    demoFormCatalogPlaceholder: "Select a range",
  },
  es: {
    localeLabel: "Idioma",
    badge: "TRYONYOU · ZERO-SIZE PROTOCOL",
    heroTitle: "El probador virtual que reduce devoluciones",
    heroLead:
      "TryOnYou crea un gemelo digital de cada cliente para simular el ajuste real de las prendas — antes de la compra.",
    heroEmailPlaceholder: "Tu email profesional",
    heroEmailPrompt: "Tu email profesional:",
    heroCta: "Solicitar Demo",
    housePhrases: [
      "No vendemos ropa. Vendemos certeza de fit.",
      "Pensado para retailers, grandes almacenes y grupos de moda.",
    ],
    inaugurationCta: "Solicitar una demo",
    inaugurationTitle: "Solicitar una demo enterprise de TryOnYou",
    inaugurationAriaLabel: "Solicitar una demo enterprise de TryOnYou",
    lafayetteCta: "Contactar con ventas",
    checkoutHint: " · demo enterprise con cita previa",
    betaCta: "Solicitar una demo",
    packStarterTitle: "Piloto retail",
    packStarterBody: "Validación rápida en un alcance acotado con KPIs de devoluciones y conversión.",
    packMaisonTitle: "Despliegue enterprise",
    packMaisonBody: "Integración omnicanal para retailers y grupos de moda multimarca.",
    videoOneTitle: "Experiencia de prueba",
    videoOneBody: "El cliente se escanea y ve el resultado antes de comprar.",
    videoTwoTitle: "Impacto de negocio",
    videoTwoBody: "El retailer reduce devoluciones, aumenta conversión y obtiene ROI medible.",
    heroSlotError: "No se ha podido enviar la solicitud ahora mismo.",
    heroSlotReserved: "Solicitud enviada. Nuestro equipo te contactará pronto.",
    heroSlotReceived: "Solicitud recibida. Te responderemos pronto.",
    bunkerOffline: "Servicio temporalmente no disponible. Inténtalo de nuevo.",
    inaugurationMissingCheckout:
      "Enlace no disponible. Usa el formulario de demo para contactar con el equipo comercial.",
    lafayetteMissingCheckout:
      "Enlace no disponible. Usa el formulario de demo para contactar con el equipo comercial.",
    ofrendaBalmain:
      "Interés registrado en el espejo digital bajo protocolo Zero-Size.",
    ofrendaReserve: "Solicitud de prueba asistida registrada.",
    ofrendaCombo: "Simulación alternativa cargada bajo protocolo Zero-Size.",
    ofrendaSave: "Silueta guardada bajo protocolo cifrado.",
    ofrendaShare: "Compartido generado con metadatos neutralizados.",
    ofrendaSelection: "Selección perfecta lista.",
    overlayReserve: "Reservar",
    overlayCombos: "Ver opciones",
    overlayMuseum: "Guardar",
    overlayShare: "Compartir",
    betaPromptEmail: "Tu email profesional (opcional):",
    betaApiError: "Error de API al guardar la solicitud.",
    betaWaitlistStored: "Solicitud guardada correctamente.",
    betaWebhookStatusOk: "ok",
    betaWebhookStatusFail: "no configurado",
    betaWebhookStatusTemplate: "Estado del webhook: {{status}}.",
    bridgeConfigured:
      "Recorrido registrado: sigue siendo necesaria la activación del servidor para los puentes comerciales.",
    bridgeLimited:
      "Recorrido registrado: sigue siendo necesaria la activación del servidor para los puentes comerciales.",
    perfectSelectionFallback:
      "Recorrido registrado: los enlaces de venta se activarán tras la configuración del servidor.",
    manifestoTag: "VISIÓN",
    manifestoTitle: "El futuro del fit no es una talla. Es una predicción.",
    manifestoBody:
      "TryOnYou convierte la prueba en infraestructura de decisión para retail moda. Sustituimos la incertidumbre por una simulación útil antes de comprar.",
    manifestoAccumulation:
      "Menos fricción, menos devoluciones y más confianza: la tecnología debe quitar complejidad, no añadirla.",
    manifestoColor:
      "El fit se vuelve medible, la decisión es más rápida y la experiencia sigue siendo deseable.",
    manifestoIdentity:
      "No vendemos un armario. Damos a los retailers la certeza que necesitan para vender mejor.",
    manifestoCta: "El comercio de moda merece certeza.",
    manifestoSlogan: "PA, PA, PA. LET'S BE THE TENDENCY. PARIS 2026.",
    manifestoHashtags: "#TryOnYou #FashionTech #RetailAI",
    manifestoLafayette: "Pilotos en curso con retailers europeos.",
    pauGuideGreeting:
      "Hola, soy P.A.U., tu asistente de fitting con IA.",
    pauGuideScan:
      "Guío al cliente durante el escaneo y la captura biométrica.",
    pauGuideSnap: "Muestro el resultado de la prenda en tiempo real.",
    pauGuideNext: "Le ayudo a decidir con certeza antes de comprar.",
    demoFormSubmitting: "Enviando…",
    demoFormSuccessTitle: "Gracias.",
    demoFormSuccessBody: "Tu solicitud de demo se ha enviado correctamente. Nuestro equipo te contactará pronto.",
    demoFormError: "No se ha podido enviar la solicitud ahora mismo.",
    demoFormRetry: "Vuelve a intentarlo en unos instantes.",
    demoFormCatalogPlaceholder: "Selecciona un rango",
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

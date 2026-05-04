export type AppLocale = "fr" | "en" | "es";

export const SUPPORTED_LOCALES: readonly AppLocale[] = ["fr", "en", "es"];

type BenefitCard = {
  eyebrow: string;
  title: string;
  body: string;
};

type SolutionStep = {
  title: string;
  body: string;
};

type TrustMetric = {
  value: string;
  label: string;
};

type DemoFieldLabels = {
  fullName: string;
  corporateEmail: string;
  company: string;
  role: string;
  businessType: string;
  primaryMarket: string;
  challenge: string;
  volume: string;
  horizon: string;
  consent: string;
};

export type SalesCopy = {
  localeLabel: string;
  nav: {
    home: string;
    technology: string;
    solutions: string;
    pilots: string;
    about: string;
    legal: string;
    demo: string;
  };
  hero: {
    title: string;
    lead: string;
    cta: string;
    trustStrip: readonly string[];
  };
  problem: {
    title: string;
    body: string;
    closing: string;
  };
  solution: {
    title: string;
    support: string;
    steps: readonly SolutionStep[];
  };
  benefits: {
    title: string;
    cards: readonly BenefitCard[];
    closing: string;
  };
  technology: {
    title: string;
    body: string;
    modules: readonly string[];
    pauLabel: string;
  };
  trust: {
    title: string;
    body: string;
    metrics: readonly TrustMetric[];
    note: string;
  };
  finalCta: {
    title: string;
    cta: string;
    microcopy: string;
  };
  demoForm: {
    title: string;
    support: string;
    submit: string;
    businessTypeOptions: readonly string[];
    fieldLabels: DemoFieldLabels;
    optionalLabel: string;
    consentHint: string;
    submitting: string;
    successTitle: string;
    successBody: string;
    error: string;
    retry: string;
  };
  footer: {
    companyLine: string;
    privacy: string;
    biometricData: string;
    terms: string;
    cookies: string;
    security: string;
  };
  expansion: {
    sectionTitle: string;
    activeBadge: string;
    pendingBadge: string;
    bannerTitle: string;
    bannerBody: string;
    locations: readonly {
      name: string;
      district: string;
      status: "active" | "pending";
    }[];
  };
  ethics: {
    sectionTitle: string;
    principles: readonly {
      title: string;
      body: string;
    }[];
    seal: string;
  };
  valuation: {
    sectionTitle: string;
    lead: string;
    arrLabel: string;
    multiplierLabel: string;
    valuationLabel: string;
    statusLabel: string;
    assetsLabel: string;
    exitLabel: string;
    monthSingular: string;
    monthPlural: string;
    reviewStatus: string;
  };
  overlayReserve: string;
  overlayCombos: string;
  overlayMuseum: string;
  overlayShare: string;
  pauGuideGreeting: string;
  pauGuideWelcome: string;
  pauGuideScan: string;
  pauGuideSnap: string;
  pauGuideNext: string;
  pauGuideClosing: string;
};

export const SALES_COPY: Record<AppLocale, SalesCopy> = {
  fr: {
    localeLabel: "Langue",
    nav: {
      home: "Home",
      technology: "Technologie",
      solutions: "Solutions",
      pilots: "Pilotes",
      about: "À propos",
      legal: "Mentions légales",
      demo: "Demander une démo",
    },
    hero: {
      title: "L'essayage virtuel qui réduit les retours et augmente la conversion.",
      lead: "TRYONYOU aide les retailers de mode à montrer le bon fit sur le vrai corps du client grâce à un jumeau numérique, un moteur de taille précis et une simulation textile réaliste.",
      cta: "Demander une démo",
      trustStrip: [
        "PCT/EP2025/067317",
        "Jusqu'à 10 000 utilisateurs simultanés",
        "99,7 % de précision biométrique déclarée",
        "Jusqu'à -85 % de retours",
      ],
    },
    problem: {
      title: "Le problème",
      body: "Chaque achat raté à cause d'une taille incorrecte érode la marge, augmente les coûts logistiques et affaiblit la confiance du client. Dans la mode, il ne suffit pas de montrer un vêtement : il faut aider le client à comprendre comment il lui ira, quelle taille il lui faut et s'il peut acheter en toute confiance.",
      closing: "La plupart des expériences de taille reposent encore sur des grilles génériques. TRYONYOU les remplace par une certitude individuelle.",
    },
    solution: {
      title: "La solution en 3 étapes",
      support: "Ce n'est pas un simple avatar. C'est un moteur de décision pour le fit, le sizing et la visualisation du vêtement pensé pour le retail enterprise.",
      steps: [
        {
          title: "Le client crée son profil corporel",
          body: "À partir d'images guidées et de données minimales, TRYONYOU génère un profil précis pour estimer les mesures et le comportement du fit.",
        },
        {
          title: "TRYONYOU crée un jumeau numérique exploitable",
          body: "Le système transforme ces informations en un modèle numérique orienté sizing, recommandation et visualisation.",
        },
        {
          title: "La marque montre la taille et l'ajustement avec clarté",
          body: "Le retailer peut recommander la bonne taille, montrer comment tombe le vêtement et réduire l'incertitude avant l'achat.",
        },
      ],
    },
    benefits: {
      title: "Bénéfices clés",
      cards: [
        {
          eyebrow: "Plus de conversion",
          title: "Moins d'hésitation au moment d'acheter",
          body: "Quand le client comprend la taille et le fit, le passage au checkout est plus probable et la PDP travaille mieux.",
        },
        {
          eyebrow: "Moins de retours",
          title: "Moins d'erreurs de taille, moins de coût opérationnel",
          body: "TRYONYOU aide à réduire les retours liés au fit et au choix de taille dans les catégories sensibles.",
        },
        {
          eyebrow: "Plus de confiance",
          title: "Une expérience plus sûre et plus utile",
          body: "La recommandation personnalisée augmente la perception de contrôle, réduit la friction et améliore la relation avec la marque.",
        },
      ],
      closing: "La promesse n'est pas seulement une meilleure expérience. La promesse est une meilleure économie unitaire par commande.",
    },
    technology: {
      title: "Technologie",
      body: "TRYONYOU combine capture guidée, modélisation corporelle, intelligence de taille et simulation de vêtement dans une seule couche de décision. Le résultat est un Digital Fit Engine capable de traduire des données visuelles et produit en recommandations de taille, représentation du fit et signaux actionnables pour le retailer.",
      modules: ["Capture", "Digital Twin", "Sizing Intelligence", "Garment Simulation"],
      pauLabel: "PAU, personal AI stylist by TRYONYOU",
    },
    trust: {
      title: "Preuve et confiance",
      body: "Une preuve sobre, orientée validation interne et déploiement enterprise.",
      metrics: [
        {
          value: "-85 %",
          label: "Jusqu'à -85 % de retours et +25 % de conversion sur des périmètres validés.",
        },
        {
          value: "99,7 %",
          label: "Précision biométrique déclarée de 99,7 %.",
        },
        {
          value: "10 000",
          label: "Architecture préparée pour jusqu'à 10 000 utilisateurs simultanés.",
        },
        {
          value: "PCT",
          label: "Zero-Size Protocol — demande internationale PCT/EP2025/067317.",
        },
      ],
      note: "Ne pas utiliser de logos sans autorisation écrite.",
    },
    finalCta: {
      title: "Si votre équipe veut réduire les retours, augmenter la conversion et valider un pilote avec un business case clair, parlons-en.",
      cta: "Demander une démo",
      microcopy: "Réponse indicative sous 48 heures ouvrées. Réunion adaptée au retail, à l'e-commerce ou aux grands magasins.",
    },
    demoForm: {
      title: "Demander une démo",
      support: "Parlez-nous de votre cas et nous préparerons une démo adaptée à votre opération, à votre canal et à votre priorité business.",
      submit: "Demander une démo",
      businessTypeOptions: ["Retailer", "E-commerce", "Grand magasin", "Marketplace"],
      fieldLabels: {
        fullName: "Nom et prénom",
        corporateEmail: "Email professionnel",
        company: "Entreprise",
        role: "Fonction",
        businessType: "Type d'activité",
        primaryMarket: "Marché principal",
        challenge: "Ce que vous voulez résoudre",
        volume: "Volume approximatif",
        horizon: "Horizon du projet",
        consent: "J'accepte d'être contacté au sujet de ma demande.",
      },
      optionalLabel: "Optionnel",
      consentHint: "Consentement de contact obligatoire.",
      submitting: "Envoi en cours…",
      successTitle: "Merci.",
      successBody: "Votre demande de démo a bien été envoyée. Notre équipe vous contactera rapidement.",
      error: "Impossible d'envoyer la demande pour le moment.",
      retry: "Veuillez réessayer dans quelques instants.",
    },
    expansion: {
      sectionTitle: "Réseau d'implantation",
      activeBadge: "Actif",
      pendingBadge: "Prochaine ouverture",
      bannerTitle: "Expansion en cours",
      bannerBody: "De nouveaux points d'expérience ouvrent leurs portes. Le réseau souverain s'étend à travers Paris.",
      locations: [
        { name: "Le Bon Marché Rive Gauche", district: "75007", status: "active" },
        { name: "Le Marais", district: "75003", status: "pending" },
        { name: "La Défense", district: "92060", status: "pending" },
      ],
    },
    ethics: {
      sectionTitle: "Manifeste éthique",
      principles: [
        {
          title: "Protection biométrique",
          body: "Les données corporelles ne quittent jamais l'appareil du client. Aucun stockage de silhouettes, aucune exploitation tierce.",
        },
        {
          title: "Transparence algorithmique",
          body: "Chaque recommandation de taille est traçable. Le client comprend pourquoi un ajustement lui est proposé.",
        },
        {
          title: "Dignité du corps",
          body: "Zéro commentaire sur le poids, zéro projection normative. Le moteur ajuste le vêtement au corps, jamais l'inverse.",
        },
        {
          title: "Souveraineté des données",
          body: "Le détaillant reçoit des signaux d'ajustement, jamais les données biométriques brutes. Le client reste propriétaire.",
        },
      ],
      seal: "Manifeste Éthique V11 — Protocole de Souveraineté",
    },
    footer: {
      companyLine: "Divineo · SIRET 94361019600017 · Paris, France",
      privacy: "Confidentialité",
      biometricData: "Données biométriques",
      terms: "Conditions",
      cookies: "Cookies",
      security: "Sécurité",
    },
    valuation: {
      sectionTitle: "Valorisation en direct",
      lead: "Scénario de marché fondé sur les hypothèses opérationnelles des nœuds parisiens et un multiplicateur ARR sectoriel, prêt pour revue financière.",
      arrLabel: "ARR projeté",
      multiplierLabel: "Multiplicateur",
      valuationLabel: "Valorisation de marché",
      statusLabel: "Statut",
      assetsLabel: "Nœuds de référence",
      exitLabel: "Horizon de sortie",
      monthSingular: "mois",
      monthPlural: "mois",
      reviewStatus: "PRÊT POUR REVUE",
    },
    overlayReserve: "Réserver",
    overlayCombos: "Voir variantes",
    overlayMuseum: "Sauvegarder",
    overlayShare: "Partager",
    pauGuideGreeting: "Bonjour, je suis PAU, personal AI stylist by TRYONYOU.",
    pauGuideWelcome:
      "Bienvenue au salon Le Bon Marché Rive Gauche, où la loyauté du Bolsillo Oculto guide chaque choix.",
    pauGuideScan: "Je guide le client dans la capture et la création de son profil corporel.",
    pauGuideSnap: "Je montre comment le vêtement tombe avant l'achat.",
    pauGuideNext: "J'aide à décider avec plus de clarté sur la taille et le fit.",
    pauGuideClosing: "Rends-le-moi avec un sourire",
  },
  en: {
    localeLabel: "Language",
    nav: {
      home: "Home",
      technology: "Technology",
      solutions: "Solutions",
      pilots: "Pilots",
      about: "About us",
      legal: "Legal",
      demo: "Request a demo",
    },
    hero: {
      title: "Virtual try-on that reduces returns and increases conversion.",
      lead: "TRYONYOU helps fashion retailers show the right fit on the customer's real body through a digital twin, precise sizing intelligence and realistic garment simulation.",
      cta: "Request a demo",
      trustStrip: [
        "PCT/EP2025/067317",
        "Up to 10,000 simultaneous users",
        "99.7% declared biometric accuracy",
        "Up to -85% returns",
      ],
    },
    problem: {
      title: "The problem",
      body: "Every failed purchase caused by incorrect sizing erodes margin, increases logistics costs and weakens customer trust. In fashion, it is not enough to show a garment: you must help the customer understand how it will fit, what size they need and whether they can buy with confidence.",
      closing: "Most sizing experiences still rely on generic charts. TRYONYOU replaces them with individual certainty.",
    },
    solution: {
      title: "The solution in 3 steps",
      support: "It is not a simple avatar. It is a decision engine for fit, sizing and garment visualization designed for enterprise retail.",
      steps: [
        {
          title: "The customer creates their body profile",
          body: "From guided images and minimal data, TRYONYOU generates a precise profile to estimate measurements and fit behavior.",
        },
        {
          title: "TRYONYOU creates a usable digital twin",
          body: "The system transforms that information into a digital model oriented to sizing, recommendation and visualization.",
        },
        {
          title: "The brand shows size and fit clearly",
          body: "The retailer can recommend the right size, show how the garment falls and reduce uncertainty before purchase.",
        },
      ],
    },
    benefits: {
      title: "Key benefits",
      cards: [
        {
          eyebrow: "More conversion",
          title: "Less doubt at the moment of purchase",
          body: "When the customer understands size and fit, the step to checkout is more likely and the PDP performs better.",
        },
        {
          eyebrow: "Fewer returns",
          title: "Fewer sizing errors, lower operating cost",
          body: "TRYONYOU helps reduce returns associated with fit and size choice in sensitive categories.",
        },
        {
          eyebrow: "More trust",
          title: "A safer and more useful experience",
          body: "Personalized recommendation increases the perception of control, reduces friction and improves the relationship with the brand.",
        },
      ],
      closing: "The promise is not only a better experience. The promise is better unit economics per order.",
    },
    technology: {
      title: "Technology",
      body: "TRYONYOU combines guided capture, body modeling, sizing intelligence and garment simulation into a single decision layer. The result is a Digital Fit Engine capable of translating visual and product data into size recommendations, fit representation and actionable signals for the retailer.",
      modules: ["Capture", "Digital Twin", "Sizing Intelligence", "Garment Simulation"],
      pauLabel: "PAU, personal AI stylist by TRYONYOU",
    },
    trust: {
      title: "Proof and trust",
      body: "A sober proof block designed for internal validation and enterprise deployment.",
      metrics: [
        {
          value: "-85%",
          label: "Up to -85% returns and +25% conversion in validated scopes.",
        },
        {
          value: "99.7%",
          label: "Declared biometric accuracy of 99.7%.",
        },
        {
          value: "10,000",
          label: "Architecture prepared for up to 10,000 simultaneous users.",
        },
        {
          value: "PCT",
          label: "Zero-Size Protocol — international filing PCT/EP2025/067317.",
        },
      ],
      note: "Do not use logos without written authorization.",
    },
    finalCta: {
      title: "If your team wants to reduce returns, increase conversion and validate a pilot with a clear business case, let's talk.",
      cta: "Request a demo",
      microcopy: "Indicative response within 48 business hours. Meeting tailored to retail, e-commerce or department stores.",
    },
    demoForm: {
      title: "Request a demo",
      support: "Tell us about your case and we will prepare a demo tailored to your operation, your channel and your business priority.",
      submit: "Request a demo",
      businessTypeOptions: ["Retailer", "E-commerce", "Department store", "Marketplace"],
      fieldLabels: {
        fullName: "Full name",
        corporateEmail: "Corporate email",
        company: "Company",
        role: "Role",
        businessType: "Business type",
        primaryMarket: "Primary market",
        challenge: "What you want to solve",
        volume: "Approximate volume",
        horizon: "Project horizon",
        consent: "I agree to be contacted regarding my request.",
      },
      optionalLabel: "Optional",
      consentHint: "Contact consent is required.",
      submitting: "Sending…",
      successTitle: "Thank you.",
      successBody: "Your demo request has been sent. Our team will contact you shortly.",
      error: "We could not send your request right now.",
      retry: "Please try again in a few moments.",
    },
    expansion: {
      sectionTitle: "Deployment network",
      activeBadge: "Active",
      pendingBadge: "Coming soon",
      bannerTitle: "Expansion underway",
      bannerBody: "New experience points are opening their doors. The sovereign network is expanding across Paris.",
      locations: [
        { name: "Le Bon Marché Rive Gauche", district: "75007", status: "active" },
        { name: "Le Marais", district: "75003", status: "pending" },
        { name: "La Défense", district: "92060", status: "pending" },
      ],
    },
    ethics: {
      sectionTitle: "Ethical manifesto",
      principles: [
        {
          title: "Biometric protection",
          body: "Body data never leaves the customer's device. No silhouette storage, no third-party exploitation.",
        },
        {
          title: "Algorithmic transparency",
          body: "Every size recommendation is traceable. The customer understands why a fit adjustment is suggested.",
        },
        {
          title: "Body dignity",
          body: "Zero weight commentary, zero normative projection. The engine fits the garment to the body, never the other way round.",
        },
        {
          title: "Data sovereignty",
          body: "The retailer receives fit signals, never raw biometric data. The customer remains the owner.",
        },
      ],
      seal: "Ethical Manifesto V11 — Sovereignty Protocol",
    },
    footer: {
      companyLine: "Divineo · SIRET 94361019600017 · Paris, France",
      privacy: "Privacy",
      biometricData: "Biometric data",
      terms: "Terms",
      cookies: "Cookies",
      security: "Security",
    },
    valuation: {
      sectionTitle: "Live valuation",
      lead: "Market scenario based on Paris node operating assumptions and a sector ARR multiplier, ready for financial review.",
      arrLabel: "Projected ARR",
      multiplierLabel: "Multiplier",
      valuationLabel: "Market valuation",
      statusLabel: "Status",
      assetsLabel: "Reference nodes",
      exitLabel: "Exit horizon",
      monthSingular: "month",
      monthPlural: "months",
      reviewStatus: "READY FOR REVIEW",
    },
    overlayReserve: "Reserve",
    overlayCombos: "View options",
    overlayMuseum: "Save",
    overlayShare: "Share",
    pauGuideGreeting: "Hello, I am PAU, personal AI stylist by TRYONYOU.",
    pauGuideWelcome:
      "Welcome to Le Bon Marché Rive Gauche, where the Hidden Pocket loyalty keeps every choice sovereign.",
    pauGuideScan: "I guide the customer through capture and body profile creation.",
    pauGuideSnap: "I show how the garment falls before purchase.",
    pauGuideNext: "I help the customer decide with more clarity on size and fit.",
    pauGuideClosing: "Rends-le-moi avec un sourire",
  },
  es: {
    localeLabel: "Idioma",
    nav: {
      home: "Home",
      technology: "Tecnología",
      solutions: "Soluciones",
      pilots: "Pilotos",
      about: "Sobre nosotros",
      legal: "Legal",
      demo: "Solicitar demo",
    },
    hero: {
      title: "El probador virtual que reduce devoluciones y aumenta la conversión.",
      lead: "TRYONYOU ayuda a los retailers de moda a mostrar el fit correcto sobre el cuerpo real del cliente mediante un gemelo digital, un motor preciso de talla y una simulación realista de la prenda.",
      cta: "Solicitar demo",
      trustStrip: [
        "PCT/EP2025/067317",
        "Hasta 10.000 usuarios simultáneos",
        "99,7 % de precisión biométrica declarada",
        "Hasta -85 % devoluciones",
      ],
    },
    problem: {
      title: "El problema",
      body: "Cada compra fallida por talla incorrecta erosiona margen, aumenta costes logísticos y debilita la confianza del cliente. En moda, no basta con mostrar una prenda: hay que ayudar al cliente a entender cómo le quedará, qué talla necesita y si puede comprar con seguridad.",
      closing: "La mayoría de las experiencias de talla siguen basándose en tablas genéricas. TRYONYOU las reemplaza por certeza individual.",
    },
    solution: {
      title: "La solución en 3 pasos",
      support: "No es un simple avatar. Es un motor de decisión para fit, sizing y visualización de prenda pensado para retail enterprise.",
      steps: [
        {
          title: "El cliente crea su perfil corporal",
          body: "A partir de imágenes guiadas y datos mínimos, TRYONYOU genera un perfil preciso para estimar medidas y comportamiento de fit.",
        },
        {
          title: "TRYONYOU crea un gemelo digital utilizable",
          body: "El sistema transforma esa información en un modelo digital orientado a sizing, recomendación y visualización.",
        },
        {
          title: "La marca muestra talla y ajuste con claridad",
          body: "El retailer puede recomendar la talla correcta, mostrar cómo cae la prenda y reducir la incertidumbre antes de la compra.",
        },
      ],
    },
    benefits: {
      title: "Beneficios clave",
      cards: [
        {
          eyebrow: "Más conversión",
          title: "Menos duda en el momento de compra",
          body: "Cuando el cliente entiende talla y fit, el paso a checkout es más probable y la PDP trabaja mejor.",
        },
        {
          eyebrow: "Menos devoluciones",
          title: "Menos errores de talla, menos coste operativo",
          body: "TRYONYOU ayuda a reducir devoluciones asociadas a fit y elección de talla en categorías sensibles.",
        },
        {
          eyebrow: "Más confianza",
          title: "Una experiencia más segura y más útil",
          body: "La recomendación personalizada aumenta la percepción de control, reduce fricción y mejora la relación con la marca.",
        },
      ],
      closing: "La promesa no es solo una mejor experiencia. La promesa es una mejor economía unitaria por pedido.",
    },
    technology: {
      title: "Tecnología",
      body: "TRYONYOU combina captura guiada, modelado corporal, inteligencia de talla y simulación de prenda en una sola capa de decisión. El resultado es un Digital Fit Engine capaz de traducir datos visuales y de producto en recomendaciones de talla, representación de fit y señales accionables para el retailer.",
      modules: ["Captura", "Digital Twin", "Sizing Intelligence", "Garment Simulation"],
      pauLabel: "PAU, personal AI stylist by TRYONYOU",
    },
    trust: {
      title: "Prueba y confianza",
      body: "Una prueba sobria, orientada a validación interna y despliegue enterprise.",
      metrics: [
        {
          value: "-85 %",
          label: "Hasta -85 % de devoluciones y +25 % de conversión en perímetros validados.",
        },
        {
          value: "99,7 %",
          label: "Precisión biométrica declarada de 99,7 %.",
        },
        {
          value: "10.000",
          label: "Arquitectura preparada para hasta 10.000 usuarios simultáneos.",
        },
        {
          value: "PCT",
          label: "Zero-Size Protocol — solicitud internacional PCT/EP2025/067317.",
        },
      ],
      note: "No usar logos sin autorización escrita.",
    },
    finalCta: {
      title: "Si su equipo quiere reducir devoluciones, aumentar conversión y validar un piloto con un caso de negocio claro, hablemos.",
      cta: "Solicitar demo",
      microcopy: "Respuesta orientativa en 48 horas laborables. Reunión adaptada a retail, e-commerce o grandes almacenes.",
    },
    demoForm: {
      title: "Solicitar demo",
      support: "Cuéntenos su caso y prepararemos una demo adaptada a su operación, su canal y su prioridad de negocio.",
      submit: "Solicitar demo",
      businessTypeOptions: ["Retailer", "E-commerce", "Gran almacén", "Marketplace"],
      fieldLabels: {
        fullName: "Nombre y apellido",
        corporateEmail: "Email corporativo",
        company: "Empresa",
        role: "Cargo",
        businessType: "Tipo de negocio",
        primaryMarket: "Mercado principal",
        challenge: "Qué quiere resolver",
        volume: "Volumen aproximado",
        horizon: "Horizonte de proyecto",
        consent: "Acepto ser contactado en relación con mi solicitud.",
      },
      optionalLabel: "Opcional",
      consentHint: "Consentimiento de contacto obligatorio.",
      submitting: "Enviando…",
      successTitle: "Gracias.",
      successBody: "Su solicitud de demo ha sido enviada. Nuestro equipo le contactará pronto.",
      error: "No hemos podido enviar su solicitud en este momento.",
      retry: "Por favor, inténtelo de nuevo en unos instantes.",
    },
    expansion: {
      sectionTitle: "Red de implantación",
      activeBadge: "Activo",
      pendingBadge: "Próxima apertura",
      bannerTitle: "Expansión en curso",
      bannerBody: "Nuevos puntos de experiencia abren sus puertas. La red soberana se extiende por París.",
      locations: [
        { name: "Le Bon Marché Rive Gauche", district: "75007", status: "active" },
        { name: "Le Marais", district: "75003", status: "pending" },
        { name: "La Défense", district: "92060", status: "pending" },
      ],
    },
    ethics: {
      sectionTitle: "Manifiesto ético",
      principles: [
        {
          title: "Protección biométrica",
          body: "Los datos corporales nunca salen del dispositivo del cliente. Sin almacenamiento de siluetas, sin explotación por terceros.",
        },
        {
          title: "Transparencia algorítmica",
          body: "Cada recomendación de talla es trazable. El cliente entiende por qué se le sugiere un ajuste.",
        },
        {
          title: "Dignidad del cuerpo",
          body: "Cero comentarios sobre peso, cero proyección normativa. El motor ajusta la prenda al cuerpo, nunca al revés.",
        },
        {
          title: "Soberanía de los datos",
          body: "El retailer recibe señales de ajuste, nunca datos biométricos brutos. El cliente sigue siendo el propietario.",
        },
      ],
      seal: "Manifiesto Ético V11 — Protocolo de Soberanía",
    },
    footer: {
      companyLine: "Divineo · SIRET 94361019600017 · París, Francia",
      privacy: "Privacidad",
      biometricData: "Datos biométricos",
      terms: "Términos",
      cookies: "Cookies",
      security: "Seguridad",
    },
    valuation: {
      sectionTitle: "Valoración en directo",
      lead: "Escenario de mercado basado en hipótesis operativas de los nodos parisinos y un multiplicador ARR sectorial, listo para revisión financiera.",
      arrLabel: "ARR proyectado",
      multiplierLabel: "Multiplicador",
      valuationLabel: "Valoración de mercado",
      statusLabel: "Estado",
      assetsLabel: "Nodos de referencia",
      exitLabel: "Horizonte de salida",
      monthSingular: "mes",
      monthPlural: "meses",
      reviewStatus: "LISTO PARA REVISIÓN",
    },
    overlayReserve: "Reservar",
    overlayCombos: "Ver variantes",
    overlayMuseum: "Guardar",
    overlayShare: "Compartir",
    pauGuideGreeting: "Hola, soy PAU, personal AI stylist by TRYONYOU.",
    pauGuideWelcome:
      "Bienvenida a Le Bon Marché Rive Gauche, donde la lealtad del Bolsillo Oculto guía cada elección.",
    pauGuideScan: "Guío al cliente en la captura y la creación de su perfil corporal.",
    pauGuideSnap: "Muestro cómo cae la prenda antes de comprar.",
    pauGuideNext: "Ayudo a decidir con más claridad sobre talla y fit.",
    pauGuideClosing: "Rends-le-moi avec un sourire",
  },
};

export function formatEurAmount(amount: number, locale: AppLocale): string {
  const localeTag = locale === "fr" ? "fr-FR" : locale === "en" ? "en-GB" : "es-ES";

  return new Intl.NumberFormat(localeTag, {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

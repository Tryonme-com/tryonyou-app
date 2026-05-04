import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import translationEN from './locales/en/translation.json';
import translationFR from './locales/fr/translation.json';
import translationES from './locales/es/translation.json';

const resources = {
  en: { translation: translationEN },
  fr: { translation: translationFR },
  es: { translation: translationES }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'fr', // Fuerza el francés como idioma de entrada para el piloto
    fallbackLng: 'en', // Sistema de respaldo en inglés
    interpolation: {
      escapeValue: false // React ya protege contra XSS
    }
  });

export default i18n;

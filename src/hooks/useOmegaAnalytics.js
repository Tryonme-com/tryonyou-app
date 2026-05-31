import { useCallback } from 'react';

export const useOmegaAnalytics = () => {
  const trackConversionEvent = useCallback((eventName, referenceId, priceTTC) => {
    const timestamp = new Date().toISOString();
    console.table([{ 
        EVENTO: eventName, 
        REFERENCIA: referenceId, 
        IMPORTE_TTC: `€${priceTTC}`, 
        HORA: timestamp 
    }]);
  }, []);

  const trackAddToCart = (referenceId, priceTTC) => trackConversionEvent('ADD_TO_CART', referenceId, priceTTC);
  return { trackAddToCart };
};
import { useState, useEffect, useCallback } from 'react';

export function useSovereignty() {
  const [licenseActive, setLicenseActive] = useState(false);
  const [fitLabel, setFitLabel] = useState('—');

  useEffect(() => {
    try {
      const raw =
        typeof __TRYONYOU_LICENSE_PAID__ !== 'undefined'
          ? __TRYONYOU_LICENSE_PAID__
          : 'false';
      const v = String(raw).toLowerCase().trim();
      setLicenseActive(v === 'true' || v === '1' || v === 'yes' || v === 'on');
    } catch {
      setLicenseActive(false);
    }
  }, []);

  const handleFitChange = useCallback((label) => {
    if (typeof label === 'string' && label.length > 0) {
      setFitLabel(label);
    }
  }, []);

  return { licenseActive, fitLabel, handleFitChange };
}

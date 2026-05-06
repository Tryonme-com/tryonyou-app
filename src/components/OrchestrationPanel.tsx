import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ORO_DIVINEO } from "../divineo/divineoV11Config";
import type { AppLocale } from "../locales/salesCopy";

type OrchestratorStatus = {
  mission: string;
  architecture: string;
  patent: string;
  engine_version: string;
  master_brands: string[];
  deployment_status: string;
  pilot_kpis: { id: string; label_fr: string; label_en: string; label_es: string }[];
};

const PANEL_COPY: Record<AppLocale, {
  title: string;
  subtitle: string;
  architecture: string;
  brands: string;
  kpis: string;
  status: string;
  live: string;
  offline: string;
  loading: string;
}> = {
  fr: {
    title: "Orchestration Globale",
    subtitle: "Moda × Technologie × Business — Pilot Lafayette",
    architecture: "Architecture",
    brands: "Maisons",
    kpis: "Piliers pilote",
    status: "Statut déploiement",
    live: "LIVE",
    offline: "Hors-ligne",
    loading: "Chargement…",
  },
  en: {
    title: "Global Orchestration",
    subtitle: "Fashion × Technology × Business — Lafayette Pilot",
    architecture: "Architecture",
    brands: "Maisons",
    kpis: "Pilot pillars",
    status: "Deployment status",
    live: "LIVE",
    offline: "Offline",
    loading: "Loading…",
  },
  es: {
    title: "Orquestación Global",
    subtitle: "Moda × Tecnología × Negocio — Piloto Lafayette",
    architecture: "Arquitectura",
    brands: "Maisons",
    kpis: "Pilares piloto",
    status: "Estado de despliegue",
    live: "LIVE",
    offline: "Sin conexión",
    loading: "Cargando…",
  },
};

type Props = {
  locale: AppLocale;
};

export function OrchestrationPanel({ locale }: Props) {
  const copy = PANEL_COPY[locale];
  const [data, setData] = useState<OrchestratorStatus | null>(null);
  const [loaded, setLoaded] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/orchestrator/status", { credentials: "same-origin" });
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch { /* offline fallback */ }
    setLoaded(true);
  }, []);

  useEffect(() => {
    void fetchStatus();
  }, [fetchStatus]);

  const kpiLabel = (kpi: { label_fr: string; label_en: string; label_es: string }) => {
    if (locale === "fr") return kpi.label_fr;
    if (locale === "es") return kpi.label_es;
    return kpi.label_en;
  };

  if (!loaded) {
    return (
      <div className="orchestration-panel orchestration-panel--loading">
        <p>{copy.loading}</p>
      </div>
    );
  }

  const isLive = data?.deployment_status === "LIVE";

  return (
    <motion.div
      className="orchestration-panel"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.5 }}
    >
      <h3 style={{ color: ORO_DIVINEO, margin: 0 }}>{copy.title}</h3>
      <p className="orchestration-panel__subtitle">{copy.subtitle}</p>

      <div className="orchestration-panel__grid">
        <div className="orchestration-panel__card">
          <span className="orchestration-panel__label">{copy.architecture}</span>
          <span className="orchestration-panel__value">
            {data?.architecture ?? "Pegaso V9.2.6"}
          </span>
        </div>

        <div className="orchestration-panel__card">
          <span className="orchestration-panel__label">{copy.status}</span>
          <span
            className="orchestration-panel__value"
            style={{ color: isLive ? "#4ade80" : "#f87171" }}
          >
            {isLive ? copy.live : copy.offline}
          </span>
        </div>

        <div className="orchestration-panel__card orchestration-panel__card--wide">
          <span className="orchestration-panel__label">{copy.brands}</span>
          <span className="orchestration-panel__value orchestration-panel__brands">
            {(data?.master_brands ?? ["BALMAIN", "DIOR", "PRADA", "CHANEL", "YSL"]).join(" · ")}
          </span>
        </div>
      </div>

      <div className="orchestration-panel__kpis">
        <span className="orchestration-panel__label">{copy.kpis}</span>
        <ul className="orchestration-panel__kpi-list">
          {(data?.pilot_kpis ?? []).map((kpi) => (
            <li key={kpi.id} className="orchestration-panel__kpi-item">
              {kpiLabel(kpi)}
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
}

import { useEffect, useState } from 'react';
import DivineMirror from './components/DivineMirror';
import Header from './components/Header';
import SnapButton from './components/SnapButton';
import { useSovereignty } from './hooks/useSovereignty';
import {
  SNAP_TAKEN,
  LEAD_SUBMITTED,
  BETA_JOINED,
  CHECKOUT_INITIATED,
} from './constants/Actions';
import { fetchJulesHealth, postMirrorSnap } from './lib/julesClient';
import { createPerfectCheckout } from './lib/shopifyCheckout';
import { OfrendaOverlay } from './components/OfrendaOverlay';
import './index.css';
import './App.css';

function elasticLabelToVerdict(label) {
  if (label.includes('Préférence drapé')) return 'drape_bias';
  if (label.includes('Préférence tenue')) return 'tension_bias';
  return 'aligned';
}

function getUrlCode() {
  try {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    return code && code.trim().length > 0 ? code.trim() : undefined;
  } catch {
    return undefined;
  }
}

async function syncLeadsToBunker(payload) {
  try {
    const response = await fetch('/api/vetos_core_inference', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...payload, system: 'BunkerV10_Santuario' }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) return { ok: false, error: data };
    if (data.status !== 'success' || data.leads_synced !== true) {
      return { ok: false, error: data };
    }
    console.log('✅ Sistema Sincronizado:', data);
    return { ok: true, data };
  } catch (error) {
    console.error('❌ Error Crítico Bunker:', error);
    return { ok: false, error };
  }
}

const OFRENDA_REVENUE_VALIDATION_EUR = 7500;
const BUNKER_BETA_PRIORITY = 0.92;

async function postLead(intent, code) {
  const payload = {
    intent,
    source: 'ofrenda_v10',
    protocol: 'zero_size',
    revenue_validation: OFRENDA_REVENUE_VALIDATION_EUR,
  };
  if (code) payload.code = code;
  console.log(LEAD_SUBMITTED, payload);
  const bunker = await syncLeadsToBunker(payload);
  if (!bunker.ok) {
    console.warn('Bunker sync no completada.', bunker.error);
    return;
  }
  try {
    const r = await fetch('/api/v1/leads', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) return;
    void (await r.json());
  } catch {
    /* hors ligne */
  }
}

async function postBetaWaitlist(code) {
  const email = window.prompt('Email (opcional) para la lista beta:', '') ?? '';
  const payload = {
    email: email.trim() || undefined,
    source: 'app_v10',
    priority: BUNKER_BETA_PRIORITY,
    vetos_priority: BUNKER_BETA_PRIORITY,
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    ts: new Date().toISOString(),
  };
  if (code) payload.code = code;
  console.log(BETA_JOINED, payload);
  try {
    const r = await fetch('/api/bunker_full_orchestrator', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) {
      window.alert('Lista beta: error de API (revisa consola).');
      return;
    }
    window.alert(
      j.waitlist_persisted
        ? `Inscrito — Make + waitlist (prioridad ${j.priority ?? BUNKER_BETA_PRIORITY}).`
        : `Make: ${j.make_ok ? 'ok' : 'no configurado / fallo'}. Waitlist puede ir a /tmp en serverless.`,
    );
  } catch {
    window.alert('Sin conexión al bunker API.');
  }
}

export default function App() {
  const { fitLabel, handleFitChange } = useSovereignty();
  const [julesLane, setJulesLane] = useState('Orchestration Jules…');
  const [emailHero, setEmailHero] = useState('');
  const urlCode = getUrlCode();

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const h = await fetchJulesHealth();
      if (cancelled) return;
      if (h?.ok) {
        setJulesLane(
          `Jules · ${h.service ?? 'omega'} · ${h.product_lane ?? 'tryonyou_v10_omega'}`,
        );
      } else {
        setJulesLane(
          'Jules · prévisualisation locale (API Python non joignable sur ce port)',
        );
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const onOfrenda = (key) => {
    if (key === 'selection') {
      console.log(CHECKOUT_INITIATED, { key, fitLabel });
      // fitLabel is used as both biometric hash proxy and fabric sensation (matches original behaviour)
      void createPerfectCheckout(fitLabel, fitLabel, urlCode);
      return;
    }
    void postLead(key, urlCode);
    const copy = {
      reserve: 'QR cabine VIP — Lafayette, essai en courtoisie Divineo.',
      combo: 'Lignes alternatives chargées — composition Zero-Size.',
      save: 'Silhouette enregistrée sous protocole chiffré (aucune taille exposée).',
      share: 'Partage généré — métadonnées d\'ajustage neutralisées.',
    };
    window.alert(copy[key]);
  };

  const theSnap = () => {
    console.log(SNAP_TAKEN, { fitLabel });
    void (async () => {
      const j = await postMirrorSnap(
        fitLabel,
        elasticLabelToVerdict(fitLabel),
        urlCode,
      );
      const msg =
        j?.jules_msg ??
        'The Snap — votre ligne trouve son équilibre. Le drapé répond avec élégance, sans mesure visible.';
      window.alert(msg);
    })();
  };

  const onHeroSubmit = async () => {
    const email = emailHero.trim();
    const normalized =
      email.length > 0 ? email : window.prompt('Email para probarla hoy:', '') ?? '';
    const finalEmail = normalized.trim();
    if (!finalEmail) return;
    const payload = {
      email: finalEmail,
      source: 'hero_above_the_fold',
      priority: BUNKER_BETA_PRIORITY,
      vetos_priority: BUNKER_BETA_PRIORITY,
      user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      ts: new Date().toISOString(),
    };
    if (urlCode) payload.code = urlCode;
    try {
      const r = await fetch('/api/bunker_full_orchestrator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) {
        window.alert('No se ha podido registrar tu slot hoy. Prueba en unos minutos.');
        return;
      }
      window.alert(
        j.waitlist_persisted || j.make_ok
          ? 'Slot reservado — webhook Make y bunker confirmados. Te contactamos hoy.'
          : 'Solicitud recibida; revisa MAKE_WEBHOOK_URL en Vercel si no llega la notificación.',
      );
    } catch {
      window.alert('Sin conexión al bunker API.');
    }
  };

  const onBrandClick = (brand) => {
    if (typeof window.tryonyouMirrorMake === 'function') {
      window.tryonyouMirrorMake(`${brand.toLowerCase()}_brand_click`);
    }
  };

  return (
    <div
      className="app-root"
      style={{
        background: 'linear-gradient(145deg, #F5F5DC 0%, #FFFFFF 38%, #D3B26A 100%)',
        color: '#111111',
      }}
    >
      <DivineMirror onFitChange={handleFitChange} />

      <div className="app-stage" aria-hidden={true} />

      <div className="app-ui">
        <Header onBrandClick={onBrandClick} />

        <section
          style={{
            padding: '32px 20px 12px',
            maxWidth: 960,
            margin: '0 auto',
          }}
        >
          <p
            style={{
              fontSize: 11,
              letterSpacing: 6,
              textTransform: 'uppercase',
              color: '#6b5b3a',
              marginBottom: 10,
            }}
          >
            TRYONYOU · DIVINEO
          </p>
          <p
            style={{
              fontSize: 13,
              letterSpacing: 3,
              textTransform: 'uppercase',
              color: '#D3B26A',
              fontStyle: 'italic',
              marginBottom: 14,
              marginTop: 0,
            }}
          >
            Essayage Virtuel en France
          </p>
          <h2
            lang="es"
            style={{
              fontSize: 'clamp(26px, 4vw, 38px)',
              lineHeight: 1.15,
              margin: 0,
              color: '#26201A',
            }}
          >
            Sabrás si te queda bien, antes de comprarlo.
          </h2>
          <p
            style={{
              marginTop: 14,
              maxWidth: 520,
              fontSize: 14,
              lineHeight: 1.7,
              color: '#4a4034',
            }}
          >
            Espejo digital en talla real. Sin probadores crueles, sin tallas que hieren.
            Solo la certeza de verte como eres antes de pagar un solo euro.
          </p>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 10,
              marginTop: 18,
              alignItems: 'center',
            }}
          >
            <input
              type="email"
              value={emailHero}
              onChange={(e) => setEmailHero(e.target.value)}
              placeholder="Tu email para probarla hoy"
              style={{
                flex: '1 1 220px',
                minWidth: 0,
                padding: '10px 14px',
                borderRadius: 999,
                border: '1px solid rgba(0,0,0,0.18)',
                fontSize: 13,
                backgroundColor: 'rgba(255,255,255,0.9)',
              }}
            />
            <button
              type="button"
              onClick={onHeroSubmit}
              style={{
                flex: '0 0 auto',
                padding: '11px 22px',
                borderRadius: 999,
                border: 'none',
                backgroundColor: '#D3B26A',
                color: '#111111',
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: 2,
                textTransform: 'uppercase',
                cursor: 'pointer',
                boxShadow: '0 10px 24px rgba(0,0,0,0.12)',
              }}
            >
              Pruébatela YA (5 slots hoy)
            </button>
          </div>
        </section>

        <OfrendaOverlay
          elasticLabel={fitLabel}
          julesLane={julesLane}
          onOfrenda={onOfrenda}
          headerExtra={
            <button
              type="button"
              onClick={() => void postBetaWaitlist(urlCode)}
              style={{
                marginTop: 14,
                padding: '8px 18px',
                fontSize: 10,
                letterSpacing: 2,
                textTransform: 'uppercase',
                color: '#C5A46D',
                background: 'rgba(0,0,0,0.5)',
                border: '1px solid #C5A46D',
                borderRadius: 999,
                cursor: 'pointer',
              }}
            >
              Únete a la beta
            </button>
          }
        />

        <SnapButton onSnap={theSnap} />
      </div>
    </div>
  );
}

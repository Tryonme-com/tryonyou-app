import React, { useState, useRef, useEffect, useCallback } from 'react';

// ─── COLLECTION DATA ────────────────────────────────────────────────────────
const COLLECTION = [
  { id: 'LAF-BAL-001', brand: 'BALMAIN', name: 'Blazer Structuré Noir Absolu', category: 'Blazer', fabric: 'Laine Mérinos', price: 2890, precision: 98.4, image: 'https://images.unsplash.com/photo-1594938298603-c8148c4b4057?w=400&q=80', tag: 'BESTSELLER' },
  { id: 'LAF-YSL-047', brand: 'SAINT LAURENT', name: 'Robe Midi Ivoire', category: 'Robe', fabric: 'Soie', price: 3450, precision: 97.9, image: 'https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400&q=80', tag: 'NOUVEAU' },
  { id: 'LAF-CHO-023', brand: 'CHLOÉ', name: 'Manteau Oversize Camel', category: 'Manteau', fabric: 'Cachemire', price: 4200, precision: 98.1, image: 'https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&q=80', tag: 'EXCLUSIF' },
  { id: 'LAF-VAL-011', brand: 'VALENTINO', name: 'Blazer Croisé Rouge', category: 'Blazer', fabric: 'Crêpe', price: 3100, precision: 97.7, image: 'https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=400&q=80', tag: 'ICONIQUE' },
  { id: 'LAF-GIV-008', brand: 'GIVENCHY', name: 'Robe Fourreau Noire', category: 'Robe', fabric: 'Crêpe de Soie', price: 3800, precision: 98.6, image: 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400&q=80', tag: 'CLASSIQUE' },
  { id: 'LAF-CEL-034', brand: 'CELINE', name: 'Trench Coat Beige', category: 'Manteau', fabric: 'Gabardine', price: 3600, precision: 97.5, image: 'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?w=400&q=80', tag: 'INTEMPOREL' },
  { id: 'LAF-ISS-019', brand: 'ISSEY MIYAKE', name: 'Robe Plissée Émeraude', category: 'Robe', fabric: 'Polyester Plissé', price: 2200, precision: 98.8, image: 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&q=80', tag: 'ARTISANAL' },
  { id: 'LAF-MCQ-055', brand: 'ALEXANDER McQUEEN', name: 'Veste Sculptée Ivoire', category: 'Veste', fabric: 'Laine Structurée', price: 4800, precision: 99.1, image: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=400&q=80', tag: 'HAUTE COUTURE' },
];

const POSE_CONNECTIONS = [
  [11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],
  [23,25],[25,27],[24,26],[26,28],[15,17],[15,19],[16,18],[16,20],
  [27,29],[27,31],[28,30],[28,32]
];

function dist(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

// ─── LANDING ────────────────────────────────────────────────────────────────
function Landing({ onStart }) {
  return (
    <div style={S.landing}>
      <div style={S.landingInner}>
        <p style={S.kicker}>Patent PCT/EP2025/067317</p>
        <h1 style={S.title}>TRYONYOU</h1>
        <p style={S.subtitle}>Zero-Size Virtual Fitting</p>
        <p style={S.desc}>Biometric pose detection eliminates numeric sizes. Your body is the only measurement that matters.</p>
        <button onClick={onStart} style={S.cta}>Start Body Scan</button>
        <div style={S.stats}>
          <Stat n="33" l="Landmarks" />
          <Stat n="99.1%" l="Precision" />
          <Stat n="0" l="Numeric Sizes" />
        </div>
      </div>
      <Footer />
    </div>
  );
}

function Stat({ n, l }) {
  return (
    <div style={S.stat}>
      <span style={S.statN}>{n}</span>
      <span style={S.statL}>{l}</span>
    </div>
  );
}

function Footer() {
  return <footer style={S.footer}>TRYONYOU — Sovereign Fit Technology</footer>;
}

// ─── BIOMETRIC SCANNER ──────────────────────────────────────────────────────
function Scanner({ onDone }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseRef = useRef(null);
  const rafRef = useRef(null);
  const [status, setStatus] = useState('init');
  const [progress, setProgress] = useState(0);
  const [fps, setFps] = useState(0);
  const frames = useRef(0);
  const lastT = useRef(performance.now());

  const init = useCallback(async () => {
    try {
      setStatus('model');
      const vision = await import(
        /* webpackIgnore: true */
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/vision_bundle.mjs'
      );
      const fileset = await vision.FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm'
      );
      poseRef.current = await vision.PoseLandmarker.createFromOptions(fileset, {
        baseOptions: {
          modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
          delegate: 'GPU'
        },
        runningMode: 'VIDEO',
        numPoses: 1
      });
      setStatus('camera');
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        setStatus('scan');
        loop();
      }
    } catch (e) {
      console.error(e);
      setStatus('error');
    }
  }, []);

  const loop = useCallback(() => {
    const v = videoRef.current;
    const p = poseRef.current;
    if (!v || !p || v.readyState < 2) { rafRef.current = requestAnimationFrame(loop); return; }

    const now = performance.now();
    const r = p.detectForVideo(v, now);
    setFps(Math.round(1000 / (now - lastT.current)));
    lastT.current = now;

    if (r.landmarks && r.landmarks.length > 0) {
      draw(r.landmarks[0]);
      frames.current++;
      setProgress(Math.min(100, Math.round((frames.current / 90) * 100)));
      if (frames.current >= 90) {
        const m = measure(r.landmarks[0]);
        v.srcObject?.getTracks().forEach(t => t.stop());
        cancelAnimationFrame(rafRef.current);
        onDone(m);
        return;
      }
    }
    rafRef.current = requestAnimationFrame(loop);
  }, [onDone]);

  const draw = (lm) => {
    const c = canvasRef.current;
    if (!c) return;
    const ctx = c.getContext('2d');
    const w = c.width, h = c.height;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(197,164,109,0.7)';
    ctx.lineWidth = 2.5;
    POSE_CONNECTIONS.forEach(([i, j]) => {
      if ((lm[i]?.visibility || 0) > 0.5 && (lm[j]?.visibility || 0) > 0.5) {
        ctx.beginPath();
        ctx.moveTo(lm[i].x * w, lm[i].y * h);
        ctx.lineTo(lm[j].x * w, lm[j].y * h);
        ctx.stroke();
      }
    });
    lm.forEach((pt, idx) => {
      if ((pt.visibility || 0) > 0.5 && idx >= 11) {
        ctx.beginPath();
        ctx.arc(pt.x * w, pt.y * h, 5, 0, Math.PI * 2);
        ctx.fillStyle = (idx >= 11 && idx <= 16) ? '#d4af37' : 'rgba(245,239,230,0.7)';
        ctx.fill();
      }
    });
  };

  const measure = (lm) => {
    const sw = dist(lm[11], lm[12]);
    const hw = dist(lm[23], lm[24]);
    const torso = dist({ x: (lm[11].x+lm[12].x)/2, y: (lm[11].y+lm[12].y)/2 }, { x: (lm[23].x+lm[24].x)/2, y: (lm[23].y+lm[24].y)/2 });
    const armL = dist(lm[11], lm[13]) + dist(lm[13], lm[15]);
    const armR = dist(lm[12], lm[14]) + dist(lm[14], lm[16]);
    const legL = dist(lm[23], lm[25]) + dist(lm[25], lm[27]);
    const legR = dist(lm[24], lm[26]) + dist(lm[26], lm[28]);
    return {
      shoulderWidth: Math.round(sw * 1000) / 10,
      hipWidth: Math.round(hw * 1000) / 10,
      torsoLength: Math.round(torso * 1000) / 10,
      armSpan: Math.round(((armL + armR) / 2) * 1000) / 10,
      legLength: Math.round(((legL + legR) / 2) * 1000) / 10,
      elasticityRatio: Math.round((sw / Math.max(hw, 0.001)) * 100) / 100,
    };
  };

  useEffect(() => { init(); return () => { cancelAnimationFrame(rafRef.current); videoRef.current?.srcObject?.getTracks().forEach(t => t.stop()); }; }, [init]);

  return (
    <div style={S.scanWrap}>
      <div style={S.scanHead}>
        <h2 style={S.scanTitle}>Biometric Scan</h2>
        <span style={S.fps}>{fps} FPS</span>
      </div>
      <div style={S.vidBox}>
        <video ref={videoRef} style={S.vid} playsInline muted />
        <canvas ref={canvasRef} width={640} height={480} style={S.cvs} />
        {status === 'scan' && <div style={S.scanLineBox}><div style={S.scanLine} /></div>}
      </div>
      <div style={S.progBar}><div style={{ ...S.progFill, width: `${progress}%` }} /></div>
      <p style={S.statusTxt}>
        {status === 'init' && 'Initializing...'}
        {status === 'model' && 'Loading AI model...'}
        {status === 'camera' && 'Activating camera...'}
        {status === 'scan' && `Scanning body vectors... ${progress}%`}
        {status === 'error' && 'Camera access required. Please allow permissions.'}
      </p>
    </div>
  );
}

// ─── CATALOGUE ──────────────────────────────────────────────────────────────
function Catalogue({ measurements, onSelect }) {
  const score = (item) => {
    if (!measurements) return item.precision;
    const r = measurements.elasticityRatio;
    if (item.category === 'Blazer' || item.category === 'Veste') return r > 0.95 ? item.precision : item.precision - (0.95 - r) * 10;
    if (item.category === 'Robe') return Math.abs(r - 1.0) < 0.15 ? item.precision : item.precision - Math.abs(r - 1.0) * 8;
    return item.precision - Math.abs(r - 1.0) * 3;
  };
  const sorted = [...COLLECTION].sort((a, b) => score(b) - score(a));

  return (
    <div style={S.catWrap}>
      <div style={S.catHead}>
        <h2 style={S.catTitle}>Curated Selection</h2>
        <p style={S.catSub}>Ranked by your biometric fit</p>
      </div>
      <div style={S.grid}>
        {sorted.map((item, i) => {
          const s = score(item);
          return (
            <div key={item.id} onClick={() => onSelect(item, s)} style={{ ...S.card, ...(i === 0 ? S.cardHero : {}) }}>
              <div style={S.cardImg}><img src={item.image} alt={item.name} style={S.img} /><span style={S.tag}>{item.tag}</span></div>
              <div style={S.cardBody}>
                <p style={S.brand}>{item.brand}</p>
                <p style={S.name}>{item.name}</p>
                <div style={S.cardFoot}>
                  <span style={S.price}>{item.price.toLocaleString()} EUR</span>
                  <span style={{ ...S.scoreLabel, color: s > 97 ? '#4ade80' : s > 95 ? '#c5a46d' : '#f87171' }}>{s.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── RESULT ─────────────────────────────────────────────────────────────────
function Result({ garment, fitScore, measurements, onBack, onRestart }) {
  const high = fitScore > 95;
  return (
    <div style={S.resWrap}>
      <div style={S.resCard}>
        <div style={S.resImgBox}>
          <img src={garment.image} alt={garment.name} style={S.resImg} />
          {high && <div style={S.resGlow} />}
        </div>
        <div style={S.resInfo}>
          <p style={S.brand}>{garment.brand}</p>
          <h2 style={S.resName}>{garment.name}</h2>
          <div style={S.fitRow}>
            <span style={{ ...S.fitNum, color: high ? '#4ade80' : '#f87171' }}>{fitScore.toFixed(1)}%</span>
            <span style={S.fitLbl}>{high ? 'Perfect Fit' : 'Custom Fit Available'}</span>
          </div>
          {high ? (
            <p style={S.resMsg}>This garment aligns perfectly with your biometric profile. Zero adjustments needed.</p>
          ) : (
            <div style={S.cap}><p style={S.capT}>Custom Atelier Production</p><p style={S.capD}>Crafting your exact fit. Zero waste.</p></div>
          )}
          <div style={S.mGrid}>
            <M l="Shoulders" v={measurements.shoulderWidth} />
            <M l="Torso" v={measurements.torsoLength} />
            <M l="Elasticity" v={measurements.elasticityRatio} />
            <M l="Fabric" v={garment.fabric} />
          </div>
          <div style={S.actions}>
            <button onClick={onBack} style={S.secBtn}>Back to Collection</button>
            <button onClick={onRestart} style={S.cta}>New Scan</button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}

function M({ l, v }) {
  return <div style={S.mItem}><span style={S.mL}>{l}</span><span style={S.mV}>{v}</span></div>;
}

// ─── APP ────────────────────────────────────────────────────────────────────
export default function App() {
  const [step, setStep] = useState('LANDING');
  const [measurements, setMeasurements] = useState(null);
  const [garment, setGarment] = useState(null);
  const [fitScore, setFitScore] = useState(0);

  return (
    <div>
      {step === 'LANDING' && <Landing onStart={() => setStep('SCAN')} />}
      {step === 'SCAN' && <Scanner onDone={(m) => { setMeasurements(m); setStep('CAT'); }} />}
      {step === 'CAT' && <Catalogue measurements={measurements} onSelect={(g, s) => { setGarment(g); setFitScore(s); setStep('RESULT'); }} />}
      {step === 'RESULT' && garment && <Result garment={garment} fitScore={fitScore} measurements={measurements} onBack={() => setStep('CAT')} onRestart={() => { setStep('LANDING'); setMeasurements(null); }} />}
    </div>
  );
}

// ─── STYLES ─────────────────────────────────────────────────────────────────
const S = {
  landing: { minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', background: 'radial-gradient(ellipse at top, #1a1d22 0%, #0d0f12 70%)' },
  landingInner: { maxWidth: '600px', textAlign: 'center', animation: 'fadeIn 0.8s ease both' },
  kicker: { fontSize: '0.72rem', letterSpacing: '3px', color: '#b8b0a4', textTransform: 'uppercase', marginBottom: '14px', fontFamily: "'Inter',sans-serif" },
  title: { fontSize: 'clamp(3rem,8vw,5rem)', color: '#c5a46d', marginBottom: '6px', letterSpacing: '6px', fontFamily: "'Cinzel',serif" },
  subtitle: { fontSize: '1.1rem', color: '#f5efe6', marginBottom: '20px', fontWeight: '300', fontFamily: "'Inter',sans-serif" },
  desc: { fontSize: '0.92rem', color: '#b8b0a4', lineHeight: '1.7', marginBottom: '36px', fontFamily: "'Inter',sans-serif" },
  cta: { background: 'linear-gradient(135deg,#c5a46d,#d4af37)', color: '#0d0f12', padding: '16px 40px', fontSize: '0.88rem', fontWeight: '600', letterSpacing: '2px', textTransform: 'uppercase', borderRadius: '6px', border: 'none', cursor: 'pointer' },
  stats: { display: 'flex', justifyContent: 'center', gap: '36px', marginTop: '48px' },
  stat: { display: 'flex', flexDirection: 'column', alignItems: 'center' },
  statN: { fontSize: '1.7rem', fontWeight: '600', color: '#c5a46d', fontFamily: "'Cinzel',serif" },
  statL: { fontSize: '0.68rem', color: '#b8b0a4', letterSpacing: '1px', marginTop: '4px', textTransform: 'uppercase', fontFamily: "'Inter',sans-serif" },
  footer: { marginTop: 'auto', paddingTop: '40px', fontSize: '0.68rem', color: '#444', letterSpacing: '2px', textAlign: 'center', fontFamily: "'Inter',sans-serif" },

  scanWrap: { minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '28px 20px', background: '#0d0f12' },
  scanHead: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', maxWidth: '660px', marginBottom: '16px' },
  scanTitle: { fontSize: '1.3rem', color: '#c5a46d', fontFamily: "'Cinzel',serif" },
  fps: { fontSize: '0.72rem', color: '#4ade80', background: '#1a1d22', padding: '4px 10px', borderRadius: '4px', fontFamily: "'Inter',sans-serif" },
  vidBox: { position: 'relative', width: '100%', maxWidth: '640px', aspectRatio: '4/3', borderRadius: '12px', overflow: 'hidden', border: '1px solid rgba(197,164,109,0.3)' },
  vid: { width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' },
  cvs: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', transform: 'scaleX(-1)', pointerEvents: 'none' },
  scanLineBox: { position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden' },
  scanLine: { position: 'absolute', left: 0, width: '100%', height: '2px', background: 'linear-gradient(90deg,transparent,#c5a46d,transparent)', animation: 'scan-line 2s linear infinite' },
  progBar: { width: '100%', maxWidth: '640px', height: '4px', background: '#1a1d22', borderRadius: '2px', marginTop: '14px', overflow: 'hidden' },
  progFill: { height: '100%', background: 'linear-gradient(90deg,#c5a46d,#d4af37)', borderRadius: '2px', transition: 'width 0.3s' },
  statusTxt: { marginTop: '10px', fontSize: '0.82rem', color: '#b8b0a4', letterSpacing: '1px', fontFamily: "'Inter',sans-serif" },

  catWrap: { minHeight: '100vh', padding: '36px 20px', maxWidth: '1100px', margin: '0 auto' },
  catHead: { textAlign: 'center', marginBottom: '36px' },
  catTitle: { fontSize: '1.9rem', color: '#c5a46d', fontFamily: "'Cinzel',serif" },
  catSub: { fontSize: '0.88rem', color: '#b8b0a4', fontFamily: "'Inter',sans-serif" },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(250px,1fr))', gap: '22px' },
  card: { background: '#1a1d22', borderRadius: '12px', overflow: 'hidden', cursor: 'pointer', border: '1px solid #252830', transition: 'transform 0.2s' },
  cardHero: { border: '1px solid rgba(197,164,109,0.5)', boxShadow: '0 0 20px rgba(197,164,109,0.12)' },
  cardImg: { position: 'relative', width: '100%', aspectRatio: '3/4', overflow: 'hidden' },
  img: { width: '100%', height: '100%', objectFit: 'cover' },
  tag: { position: 'absolute', top: '8px', right: '8px', background: 'rgba(13,15,18,0.85)', color: '#c5a46d', fontSize: '0.58rem', padding: '3px 7px', borderRadius: '3px', letterSpacing: '1px', fontFamily: "'Inter',sans-serif" },
  cardBody: { padding: '14px' },
  brand: { fontSize: '0.68rem', color: '#b8b0a4', letterSpacing: '2px', textTransform: 'uppercase', marginBottom: '3px', fontFamily: "'Inter',sans-serif" },
  name: { fontSize: '0.92rem', color: '#f5efe6', marginBottom: '10px', fontFamily: "'Inter',sans-serif" },
  cardFoot: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  price: { fontSize: '0.82rem', color: '#f5efe6', fontWeight: '500', fontFamily: "'Inter',sans-serif" },
  scoreLabel: { fontSize: '0.78rem', fontWeight: '600', fontFamily: "'Inter',sans-serif" },

  resWrap: { minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '36px 20px' },
  resCard: { display: 'flex', flexWrap: 'wrap', gap: '36px', maxWidth: '880px', width: '100%', animation: 'fadeIn 0.6s ease both' },
  resImgBox: { position: 'relative', flex: '1 1 280px', minHeight: '380px', borderRadius: '12px', overflow: 'hidden' },
  resImg: { width: '100%', height: '100%', objectFit: 'cover', borderRadius: '12px' },
  resGlow: { position: 'absolute', inset: 0, borderRadius: '12px', boxShadow: 'inset 0 0 40px rgba(212,175,55,0.3)', pointerEvents: 'none' },
  resInfo: { flex: '1 1 280px', display: 'flex', flexDirection: 'column', justifyContent: 'center' },
  resName: { fontSize: '1.7rem', color: '#f5efe6', margin: '6px 0 18px', fontFamily: "'Cinzel',serif" },
  fitRow: { display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '18px' },
  fitNum: { fontSize: '2.4rem', fontWeight: '700', fontFamily: "'Cinzel',serif" },
  fitLbl: { fontSize: '0.82rem', color: '#b8b0a4', fontFamily: "'Inter',sans-serif" },
  resMsg: { fontSize: '0.88rem', color: '#b8b0a4', lineHeight: '1.6', marginBottom: '22px', fontFamily: "'Inter',sans-serif" },
  cap: { background: '#1a1d22', border: '1px solid #252830', borderRadius: '8px', padding: '14px', marginBottom: '22px' },
  capT: { fontSize: '0.76rem', color: '#c5a46d', letterSpacing: '1px', marginBottom: '4px', textTransform: 'uppercase', fontFamily: "'Inter',sans-serif" },
  capD: { fontSize: '0.82rem', color: '#b8b0a4', fontFamily: "'Inter',sans-serif" },
  mGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '26px' },
  mItem: { background: '#1a1d22', borderRadius: '8px', padding: '10px', display: 'flex', flexDirection: 'column' },
  mL: { fontSize: '0.62rem', color: '#b8b0a4', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '3px', fontFamily: "'Inter',sans-serif" },
  mV: { fontSize: '1.05rem', color: '#f5efe6', fontWeight: '500', fontFamily: "'Inter',sans-serif" },
  actions: { display: 'flex', gap: '12px', flexWrap: 'wrap' },
  secBtn: { background: 'transparent', color: '#c5a46d', border: '1px solid #c5a46d', padding: '12px 22px', fontSize: '0.82rem', fontWeight: '500', borderRadius: '6px', letterSpacing: '1px', cursor: 'pointer', fontFamily: "'Inter',sans-serif" },
};

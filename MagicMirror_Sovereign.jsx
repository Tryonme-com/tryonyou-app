import React, { useState } from 'react';

const MagicMirror = () => {
  const [fase, setFase] = useState('inicio');

  const iniciarScan = () => {
    setFase('escaneo');
    setTimeout(() => setFase('seleccion'), 14000);
  };

  return (
    <div style={{ background: '#000', color: '#fff', height: '100vh', textAlign: 'center', fontFamily: 'serif' }}>
      {fase === 'inicio' && (
        <button onClick={iniciarScan} style={{ marginTop: '40vh', padding: '20px 50px', background: 'none', border: '1px solid #fff', color: '#fff', cursor: 'pointer' }}>
          ACTIVER L'EXPÉRIENCE SOUVERAINE
        </button>
      )}
      
      {fase === 'escaneo' && (
        <div style={{ paddingTop: '30vh' }}>
          <div style={{ width: '100%', height: '2px', background: '#fff', boxShadow: '0 0 20px #fff', animation: 'scan 3s infinite' }}></div>
          <p style={{ letterSpacing: '5px', marginTop: '20px' }}>ANALYSE BIOMÉTRIQUE V10 (SANS DONNÉES INTRUSIVES)</p>
        </div>
      )}

      {fase === 'seleccion' && (
        <div style={{ paddingTop: '10vh' }}>
          <h2>VOTRE SÉLECTION PAR P.A.U.</h2>
          <p>Le système a sculpté votre silhouette.</p>
        </div>
      )}
      <style>{`@keyframes scan { 0% { transform: translateY(0); } 50% { transform: translateY(40vh); } 100% { transform: translateY(0); } }`}</style>
    </div>
  );
};
export default MagicMirror;

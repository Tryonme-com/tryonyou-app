import React, { useState } from 'react';

export default function App() {
  const [step, setStep] = useState('LANDING');

  return (
    <div style={{ backgroundColor: '#141619', minHeight: '100vh', color: '#F5F5DC', fontFamily: 'serif', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px', textAlign: 'center' }}>
      
      {step === 'LANDING' && (
        <div style={{ maxWidth: '600px' }}>
          <h1 style={{ color: '#C5A46D', fontSize: '3.5rem', letterSpacing: '4px', marginBottom: '20px' }}>TRYONYOU</h1>
          <p style={{ fontSize: '1.2rem', marginBottom: '40px' }}>El e-commerce falla en el 40% de los casos. Descubre tu Fit perfecto.</p>
          <button onClick={() => setStep('SCANNING')} style={{ backgroundColor: '#C5A46D', color: '#000', padding: '15px 30px', border: 'none', fontWeight: 'bold', letterSpacing: '2px', cursor: 'pointer', textTransform: 'uppercase' }}>
            Activar Escáner Biométrico
          </button>
        </div>
      )}

      {step === 'SCANNING' && (
        <div style={{ border: '2px solid #C5A46D', borderRadius: '10px', padding: '40px', maxWidth: '600px', width: '100%' }}>
          <h2 style={{ color: '#C5A46D', fontSize: '1.8rem', letterSpacing: '2px', marginBottom: '20px' }}>CALIBRANDO SILUETA...</h2>
          <p style={{ marginBottom: '30px', color: '#888' }}>Escaneando vectores corporales en tiempo real. Aplicando reglas de elasticidad.</p>
          <button onClick={() => setStep('RESULT')} style={{ backgroundColor: '#C5A46D', color: '#000', padding: '12px 24px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>
            Aplicar Prenda (Fit Engine)
          </button>
        </div>
      )}

      {step === 'RESULT' && (
        <div style={{ maxWidth: '600px' }}>
          <h3 style={{ color: '#C5A46D', fontSize: '2.5rem', marginBottom: '20px' }}>AJUSTEMENT PARFAIT</h3>
          <p style={{ fontSize: '1.2rem', marginBottom: '10px' }}>✓ Precisión Biométrica: 99.7%</p>
          <p style={{ fontSize: '1rem', color: '#888', marginBottom: '40px' }}>Filosofía Zero-Size Activa: Zéro Taille. Zéro Chiffre.</p>
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button style={{ backgroundColor: '#C5A46D', color: '#000', padding: '12px 20px', border: 'none', fontWeight: 'bold', cursor: 'pointer' }}>1. Mi Selección Perfecta</button>
            <button style={{ backgroundColor: 'transparent', color: '#C5A46D', border: '1px solid #C5A46D', padding: '12px 20px', fontWeight: 'bold', cursor: 'pointer' }}>2. Reservar en Tienda (QR)</button>
          </div>
        </div>
      )}
      
      <div style={{ marginTop: '50px', fontSize: '0.8rem', color: '#666', letterSpacing: '2px' }}>
        Patente PCT/EP2025/067317 • Piloto Lafayette V9
      </div>
    </div>
  );
}

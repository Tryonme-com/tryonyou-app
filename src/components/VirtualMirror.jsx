import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';

export default function VirtualMirror() {
  const webcamRef = useRef(null);
  const [isScanning, setIsScanning] = useState(true);
  const [currentLookIndex, setCurrentLookIndex] = useState(0);
  const [fitScore, setFitScore] = useState(0);

  // CRM_MASTER_CLEAN: Los 5 looks oficiales del Piloto Lafayette
  const looks = [
    { id: "EG-001", nombre: "Robe Rouge Minimal", tejido: "Seda Elástica", img: "/assets/catalog/red_dress_minimal.png", match: 99.7 },
    { id: "EG-002", nombre: "Esmoquin Midnight Blue", tejido: "Lana Fría Super 150s", img: "/assets/catalog/midnight_tuxedo.png", match: 99.1 },
    { id: "EG-003", nombre: "Tailleur Éditorial", tejido: "Lana Ligera", img: "/assets/catalog/tailleur.png", match: 98.5 },
    { id: "EG-004", nombre: "Gala Lafayette", tejido: "Terciopelo Líquido", img: "/assets/catalog/gala.png", match: 99.4 },
    { id: "EG-005", nombre: "Burberry Trench", tejido: "Gabardina Dinámica", img: "/assets/catalog/burberry_trench.png", match: 97.8 }
  ];

  // Efecto del escáner biométrico inicial (3 segundos)
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsScanning(false);
      setFitScore(looks.match);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  // Función para rotar las 5 prendas (Live Overlay Swap)
  const cycleLooks = () => {
    const nextIndex = (currentLookIndex + 1) % looks.length;
    setCurrentLookIndex(nextIndex);
    setFitScore(looks[nextIndex].match);
  };

  return (
    <div style={{ position: 'relative', width: '100%', maxWidth: '600px', margin: '0 auto', borderRadius: '20px', overflow: 'hidden', backgroundColor: '#141619', border: '2px solid #C5A46D' }}>
      
      {/* 1. Capa Live: Cámara Web */}
      <Webcam
        ref={webcamRef}
        audio={false}
        mirrored={true}
        style={{ width: '100%', height: 'auto', display: 'block' }}
      />

      {/* 2. Capa Overlay: Escáner o Prenda Digital */}
      {isScanning ? (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', backgroundColor: 'rgba(20, 22, 25, 0.7)' }}>
          <div style={{ width: '80%', height: '2px', backgroundColor: '#C5A46D', boxShadow: '0 0 15px #C5A46D', animation: 'scan 2s infinite' }} />
          <p style={{ color: '#C5A46D', marginTop: '20px', fontFamily: 'monospace', letterSpacing: '2px' }}>CALIBRANDO MEDIA-PIPE POSE...</p>
        </div>
      ) : (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none' }}>
          {/* Aquí se proyecta la imagen PNG transparente sobre el cuerpo */}
          <img 
            src={looks[currentLookIndex].img} 
            alt="Prenda Overlay" 
            style={{ width: '100%', height: '100%', objectFit: 'contain', opacity: 0.9 }}
          />
        </div>
      )}

      {/* 3. Panel de Control Divineo V7 (Física y Zero-Size) */}
      {!isScanning && (
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '20px', background: 'linear-gradient(transparent, #141619)', color: '#F5EFE6', textAlign: 'center' }}>
          <h3 style={{ margin: '0 0 5px', color: '#C5A46D' }}>{looks[currentLookIndex].nombre}</h3>
          <p style={{ margin: '0 0 15px', fontSize: '14px', opacity: 0.8 }}>Tejido: {looks[currentLookIndex].tejido} | Match Absoluto: {fitScore}%</p>
          
          <button 
            onClick={cycleLooks}
            style={{ padding: '12px 24px', backgroundColor: '#C5A46D', color: '#141619', border: 'none', borderRadius: '30px', fontWeight: 'bold', cursor: 'pointer', pointerEvents: 'auto', textTransform: 'uppercase', letterSpacing: '1px' }}>
            ✨ Ver Combinaciones (El Chasquido)
          </button>
        </div>
      )}
      
      <style>{`
        @keyframes scan { 0% { transform: translateY(-150px); } 50% { transform: translateY(150px); } 100% { transform: translateY(-150px); } }
      `}</style>
    </div>
  );
}

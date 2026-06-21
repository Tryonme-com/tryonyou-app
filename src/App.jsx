import React, { useState, useEffect, useRef } from 'react';

export default function App() {
  const [step, setStep] = useState('LANDING');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (step !== 'SCANNING' || !videoRef.current || !canvasRef.current) return;

    // Inicialización dinámica de los scripts de MediaPipe para evitar bloqueos
    let pose;
    let camera;

    const loadMediaPipe = async () => {
      try {
        pose = new window.Pose({
          locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        });

        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        });

        pose.onResults((results) => {
          if (!canvasRef.current) return;
          const ctx = canvasRef.current.getContext('2d');
          ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          
          if (results.poseLandmarks) {
            // Capa Robert Engine: Simulación física elemental sobre landmarks
            ctx.fillStyle = '#C5A46D';
            results.poseLandmarks.forEach((landmark) => {
              const x = landmark.x * canvasRef.current.width;
              const y = landmark.y * canvasRef.current.height;
              ctx.beginPath();
              ctx.arc(x, y, 4, 0, 2 * Math.PI);
              ctx.fill();
            });
          }
        });

        camera = new window.Camera(videoRef.current, {
          onFrame: async () => {
            if (videoRef.current && pose) {
              await pose.send({ image: videoRef.current });
            }
          },
          width: 640,
          height: 480
        });
        camera.start();
      } catch (err) {
        console.error("Error al inicializar hardware biométrico:", err);
      }
    };

    loadMediaPipe();

    return () => {
      if (camera) camera.stop();
      if (pose) pose.close();
    };
  }, [step]);

  return (
    <div style={{ backgroundColor: '#141619', minHeight: '100vh', color: '#F5F5F5', padding: '40px', fontFamily: 'sans-serif' }}>
      {step === 'LANDING' && (
        <div style={{ maxWidth: '600px' }}>
          <h1 style={{ color: '#C5A46D', fontSize: '3.5rem', letterSpacing: '4px' }}>TRYONYOU</h1>
          <p style={{ fontSize: '1.2rem', marginBottom: '40px' }}>Colección Lafayette - Robert Engine Activo</p>
          <button onClick={() => setStep('SCANNING')} style={{ backgroundColor: '#C5A46D', color: '#141619', border: 'none', padding: '15px 30px', fontSize: '1rem', cursor: 'pointer', fontWeight: 'bold' }}>
            Activar Escáner Biométrico
          </button>
        </div>
      )}

      {step === 'SCANNING' && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <h2 style={{ color: '#C5A46D', marginBottom: '20px' }}>Miroir Digital Actif</h2>
          <div style={{ position: 'relative', width: '640px', height: '480px', backgroundColor: '#000', borderRadius: '8px', overflow: 'hidden' }}>
            <video ref={videoRef} style={{ position: 'absolute', top: 0, left: 0, width: '640px', height: '480px', objectFit: 'cover', zIndex: 10 }} playsInline muted autoPlay />
            <canvas ref={canvasRef} width="640" height="480" style={{ position: 'absolute', top: 0, left: 0, width: '640px', height: '480px', zIndex: 20, pointerEvents: 'none' }} />
          </div>
          <button onClick={() => setStep('LANDING')} style={{ marginTop: '20px', backgroundColor: 'transparent', color: '#888', border: '

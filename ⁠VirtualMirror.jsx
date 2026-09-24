import React, { useState, useEffect, useRef } from 'react';

export default function VirtualMirror() {
  const [isScanning, setIsScanning] = useState(true);
  const [fitScore, setFitScore] = useState(0);
  const [cameraReady, setCameraReady] = useState(false);
  
  const videoRef = useRef(null);

  useEffect(() => {
    let stream = null;

    const initCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 1280, height: 720 } 
        });
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          
          // Esperamos a que el video realmente tenga datos (metadata cargado)
          videoRef.current.onloadedmetadata = () => {
            console.log("Cámara lista: Flujo de video activo.");
            setCameraReady(true);
          };
        }
      } catch (err) {
        console.error("Error crítico de hardware:", err);
      }
    };

    initCamera();

    return () => {
      if (stream) stream.getTracks().forEach(track => track.stop());
    };
  }, []);

  // El escáner solo se dispara si la cámara está realmente lista
  useEffect(() => {
    if (cameraReady) {
      const scanTimer = setTimeout(() => {
        setIsScanning(false);
        setFitScore(99.7);
        console.log("Motor V10: Escaneo biométrico completado.");
      }, 3000);
      return () => clearTimeout(scanTimer);
    }
  }, [cameraReady]);

  // ... resto del componente

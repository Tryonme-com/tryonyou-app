import React, { useState, useRef, useEffect, useCallback } from 'react';

/**
 * VirtualMirror.jsx - TRYONYOU Biometric Pose Detection
 * 
 * Real integration of MediaPipe Pose Landmarker (@mediapipe/tasks-vision)
 * Detects 33 body landmarks in real-time from webcam feed and draws
 * the biometric skeleton overlay on a canvas layer.
 * 
 * Architecture:
 * 1. Video layer: Raw webcam feed via getUserMedia
 * 2. Canvas layer: Skeleton overlay drawn with detected landmarks
 * 3. UI layer: Controls and fit information
 * 
 * Dependencies: @mediapipe/tasks-vision (loaded via CDN for WASM compatibility)
 */

// MediaPipe Pose Landmark connections for drawing the skeleton
// Each pair [startIdx, endIdx] represents a bone/connection
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7],   // Right face
  [0, 4], [4, 5], [5, 6], [6, 8],   // Left face
  [9, 10],                            // Mouth
  [11, 12],                           // Shoulders
  [11, 13], [13, 15],                // Left arm
  [12, 14], [14, 16],                // Right arm
  [15, 17], [15, 19], [15, 21],      // Left hand
  [16, 18], [16, 20], [16, 22],      // Right hand
  [17, 19], [18, 20],                // Hand connections
  [11, 23], [12, 24],                // Torso
  [23, 24],                           // Hips
  [23, 25], [25, 27],                // Left leg
  [24, 26], [26, 28],                // Right leg
  [27, 29], [29, 31], [27, 31],      // Left foot
  [28, 30], [30, 32], [28, 32],      // Right foot
];

// Landmark indices for key body measurements
const LANDMARK_NAMES = {
  NOSE: 0,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
};

export default function VirtualMirror() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const poseLandmarkerRef = useRef(null);
  const animationFrameRef = useRef(null);
  const lastVideoTimeRef = useRef(-1);

  const [isLoading, setIsLoading] = useState(true);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [landmarks, setLandmarks] = useState(null);
  const [bodyMeasurements, setBodyMeasurements] = useState(null);
  const [showSkeleton, setShowSkeleton] = useState(true);
  const [showMeasurements, setShowMeasurements] = useState(true);
  const [fps, setFps] = useState(0);
  const fpsCounterRef = useRef({ frames: 0, lastTime: performance.now() });

  /**
   * Initialize MediaPipe Pose Landmarker via CDN
   * Uses the @mediapipe/tasks-vision package with WASM backend
   */
  const initializePoseLandmarker = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Dynamically import MediaPipe tasks-vision from CDN
      const vision = await import(
        /* webpackIgnore: true */
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/vision_bundle.mjs'
      );

      const { PoseLandmarker, FilesetResolver } = vision;

      // Initialize WASM fileset
      const filesetResolver = await FilesetResolver.forVisionTasks(
        'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
      );

      // Create PoseLandmarker with optimized settings for real-time detection
      const landmarker = await PoseLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath:
            'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task',
          delegate: 'GPU', // Use GPU acceleration when available
        },
        runningMode: 'VIDEO',
        numPoses: 1,
        minPoseDetectionConfidence: 0.5,
        minPosePresenceConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      poseLandmarkerRef.current = landmarker;
      setIsLoading(false);
      console.log('[VirtualMirror] PoseLandmarker initialized successfully');
    } catch (err) {
      console.error('[VirtualMirror] Failed to initialize PoseLandmarker:', err);
      setError(`Failed to load pose detection model: ${err.message}`);
      setIsLoading(false);
    }
  }, []);

  /**
   * Start webcam stream via getUserMedia API
   */
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
          frameRate: { ideal: 30 },
        },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        console.log('[VirtualMirror] Camera started');
      }
    } catch (err) {
      console.error('[VirtualMirror] Camera access denied:', err);
      setError('Camera access denied. Please allow camera permissions.');
    }
  }, []);

  /**
   * Calculate body measurements from detected landmarks
   * Returns shoulder width, torso length, arm span in relative units
   */
  const calculateMeasurements = useCallback((poseLandmarks) => {
    if (!poseLandmarks || poseLandmarks.length < 33) return null;

    const lm = poseLandmarks;

    // Euclidean distance helper (2D normalized coordinates)
    const dist = (a, b) => {
      const dx = lm[a].x - lm[b].x;
      const dy = lm[a].y - lm[b].y;
      return Math.sqrt(dx * dx + dy * dy);
    };

    // Key measurements (normalized 0-1 scale)
    const shoulderWidth = dist(LANDMARK_NAMES.LEFT_SHOULDER, LANDMARK_NAMES.RIGHT_SHOULDER);
    const torsoLength = dist(
      (LANDMARK_NAMES.LEFT_SHOULDER + LANDMARK_NAMES.RIGHT_SHOULDER) / 2 | 0,
      (LANDMARK_NAMES.LEFT_HIP + LANDMARK_NAMES.RIGHT_HIP) / 2 | 0
    );
    // More accurate torso: average of left and right side
    const leftTorso = dist(LANDMARK_NAMES.LEFT_SHOULDER, LANDMARK_NAMES.LEFT_HIP);
    const rightTorso = dist(LANDMARK_NAMES.RIGHT_SHOULDER, LANDMARK_NAMES.RIGHT_HIP);
    const avgTorso = (leftTorso + rightTorso) / 2;

    const leftArm = dist(LANDMARK_NAMES.LEFT_SHOULDER, LANDMARK_NAMES.LEFT_ELBOW) +
                    dist(LANDMARK_NAMES.LEFT_ELBOW, LANDMARK_NAMES.LEFT_WRIST);
    const rightArm = dist(LANDMARK_NAMES.RIGHT_SHOULDER, LANDMARK_NAMES.RIGHT_ELBOW) +
                     dist(LANDMARK_NAMES.RIGHT_ELBOW, LANDMARK_NAMES.RIGHT_WRIST);

    const hipWidth = dist(LANDMARK_NAMES.LEFT_HIP, LANDMARK_NAMES.RIGHT_HIP);

    const leftLeg = dist(LANDMARK_NAMES.LEFT_HIP, LANDMARK_NAMES.LEFT_KNEE) +
                    dist(LANDMARK_NAMES.LEFT_KNEE, LANDMARK_NAMES.LEFT_ANKLE);
    const rightLeg = dist(LANDMARK_NAMES.RIGHT_HIP, LANDMARK_NAMES.RIGHT_KNEE) +
                     dist(LANDMARK_NAMES.RIGHT_KNEE, LANDMARK_NAMES.RIGHT_ANKLE);

    return {
      shoulderWidth: (shoulderWidth * 100).toFixed(1),
      torsoLength: (avgTorso * 100).toFixed(1),
      hipWidth: (hipWidth * 100).toFixed(1),
      leftArm: (leftArm * 100).toFixed(1),
      rightArm: (rightArm * 100).toFixed(1),
      leftLeg: (leftLeg * 100).toFixed(1),
      rightLeg: (rightLeg * 100).toFixed(1),
      // Proportional ratio for fit calculation
      shoulderToHipRatio: (shoulderWidth / hipWidth).toFixed(2),
      torsoToLegRatio: (avgTorso / ((leftLeg + rightLeg) / 2)).toFixed(2),
    };
  }, []);

  /**
   * Draw pose landmarks and skeleton connections on canvas
   * This is the core rendering function called every frame
   */
  const drawPose = useCallback((poseLandmarks, canvas) => {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear previous frame
    ctx.clearRect(0, 0, width, height);

    if (!poseLandmarks || poseLandmarks.length === 0) return;

    const lm = poseLandmarks;

    // Draw skeleton connections (bones)
    if (showSkeleton) {
      ctx.strokeStyle = '#C5A46D'; // TRYONYOU gold
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';
      ctx.shadowColor = '#C5A46D';
      ctx.shadowBlur = 6;

      for (const [startIdx, endIdx] of POSE_CONNECTIONS) {
        const start = lm[startIdx];
        const end = lm[endIdx];

        // Only draw if both landmarks are visible enough
        if (start.visibility > 0.5 && end.visibility > 0.5) {
          ctx.beginPath();
          ctx.moveTo(start.x * width, start.y * height);
          ctx.lineTo(end.x * width, end.y * height);
          ctx.stroke();
        }
      }

      // Draw landmark points
      ctx.shadowBlur = 0;
      for (let i = 0; i < lm.length; i++) {
        const landmark = lm[i];
        if (landmark.visibility > 0.5) {
          // Key landmarks (shoulders, hips) get larger dots
          const isKeyLandmark = [11, 12, 23, 24, 0].includes(i);
          const radius = isKeyLandmark ? 6 : 3;

          ctx.beginPath();
          ctx.arc(landmark.x * width, landmark.y * height, radius, 0, 2 * Math.PI);
          ctx.fillStyle = isKeyLandmark ? '#FFFFFF' : '#C5A46D';
          ctx.fill();

          if (isKeyLandmark) {
            ctx.strokeStyle = '#C5A46D';
            ctx.lineWidth = 2;
            ctx.stroke();
          }
        }
      }
    }

    // Draw measurement lines if enabled
    if (showMeasurements && lm[LANDMARK_NAMES.LEFT_SHOULDER].visibility > 0.5) {
      ctx.setLineDash([5, 5]);
      ctx.strokeStyle = 'rgba(197, 164, 109, 0.6)';
      ctx.lineWidth = 1;

      // Shoulder line
      const ls = lm[LANDMARK_NAMES.LEFT_SHOULDER];
      const rs = lm[LANDMARK_NAMES.RIGHT_SHOULDER];
      ctx.beginPath();
      ctx.moveTo(ls.x * width, ls.y * height);
      ctx.lineTo(rs.x * width, rs.y * height);
      ctx.stroke();

      // Hip line
      const lh = lm[LANDMARK_NAMES.LEFT_HIP];
      const rh = lm[LANDMARK_NAMES.RIGHT_HIP];
      ctx.beginPath();
      ctx.moveTo(lh.x * width, lh.y * height);
      ctx.lineTo(rh.x * width, rh.y * height);
      ctx.stroke();

      ctx.setLineDash([]);
    }
  }, [showSkeleton, showMeasurements]);

  /**
   * Main detection loop - runs every animation frame
   * Sends video frame to PoseLandmarker and processes results
   */
  const detectPose = useCallback(() => {
    if (!poseLandmarkerRef.current || !videoRef.current) {
      animationFrameRef.current = requestAnimationFrame(detectPose);
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.readyState < 2) {
      animationFrameRef.current = requestAnimationFrame(detectPose);
      return;
    }

    // Match canvas size to video
    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    const currentTime = video.currentTime;
    if (currentTime !== lastVideoTimeRef.current) {
      lastVideoTimeRef.current = currentTime;

      try {
        // Core MediaPipe detection call
        const result = poseLandmarkerRef.current.detectForVideo(video, performance.now());

        if (result && result.landmarks && result.landmarks.length > 0) {
          const poseLandmarks = result.landmarks[0]; // First detected pose
          setLandmarks(poseLandmarks);
          drawPose(poseLandmarks, canvas);

          // Calculate body measurements
          const measurements = calculateMeasurements(poseLandmarks);
          if (measurements) {
            setBodyMeasurements(measurements);
          }
        } else {
          // No pose detected - clear canvas
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          setLandmarks(null);
          setBodyMeasurements(null);
        }
      } catch (err) {
        console.warn('[VirtualMirror] Detection frame error:', err.message);
      }
    }

    // FPS counter
    fpsCounterRef.current.frames++;
    const now = performance.now();
    if (now - fpsCounterRef.current.lastTime >= 1000) {
      setFps(fpsCounterRef.current.frames);
      fpsCounterRef.current.frames = 0;
      fpsCounterRef.current.lastTime = now;
    }

    animationFrameRef.current = requestAnimationFrame(detectPose);
  }, [drawPose, calculateMeasurements]);

  /**
   * Start the full pipeline: model + camera + detection loop
   */
  const startDetection = useCallback(async () => {
    await initializePoseLandmarker();
    await startCamera();
    setIsDetecting(true);
  }, [initializePoseLandmarker, startCamera]);

  /**
   * Effect: Start detection loop once isDetecting is true
   */
  useEffect(() => {
    if (isDetecting && poseLandmarkerRef.current) {
      animationFrameRef.current = requestAnimationFrame(detectPose);
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isDetecting, detectPose]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = videoRef.current.srcObject.getTracks();
        tracks.forEach((track) => track.stop());
      }
      if (poseLandmarkerRef.current) {
        poseLandmarkerRef.current.close();
      }
    };
  }, []);

  // ─── RENDER ────────────────────────────────────────────────────────────────

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '700px',
        margin: '0 auto',
        borderRadius: '16px',
        overflow: 'hidden',
        backgroundColor: '#141619',
        border: '2px solid #C5A46D',
        boxShadow: '0 0 40px rgba(197, 164, 109, 0.15)',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '12px 20px',
          background: 'linear-gradient(90deg, #1a1c20, #141619)',
          borderBottom: '1px solid rgba(197, 164, 109, 0.3)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span style={{ color: '#C5A46D', fontFamily: 'monospace', fontSize: '12px', letterSpacing: '2px' }}>
          TRYONYOU BIOMETRIC ENGINE
        </span>
        {isDetecting && (
          <span style={{ color: '#4CAF50', fontFamily: 'monospace', fontSize: '11px' }}>
            ● LIVE {fps} FPS
          </span>
        )}
      </div>

      {/* Video + Canvas Container */}
      <div style={{ position: 'relative', width: '100%', aspectRatio: '4/3', backgroundColor: '#000' }}>
        {/* Webcam video feed */}
        <video
          ref={videoRef}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            transform: 'scaleX(-1)', // Mirror mode
            display: isDetecting ? 'block' : 'none',
          }}
          playsInline
          muted
        />

        {/* Canvas overlay for skeleton drawing */}
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            transform: 'scaleX(-1)', // Mirror to match video
            pointerEvents: 'none',
          }}
        />

        {/* Loading state */}
        {isLoading && isDetecting && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(20, 22, 25, 0.9)',
            }}
          >
            <div
              style={{
                width: '60%',
                height: '2px',
                backgroundColor: '#C5A46D',
                boxShadow: '0 0 15px #C5A46D',
                animation: 'scan 2s infinite',
              }}
            />
            <p style={{ color: '#C5A46D', marginTop: '20px', fontFamily: 'monospace', letterSpacing: '2px', fontSize: '13px' }}>
              LOADING MEDIAPIPE POSE MODEL...
            </p>
            <p style={{ color: '#888', marginTop: '8px', fontFamily: 'monospace', fontSize: '11px' }}>
              Downloading WASM + ML model (~4MB)
            </p>
          </div>
        )}

        {/* Initial state - before starting */}
        {!isDetecting && !error && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#141619',
              padding: '40px',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '20px', opacity: 0.8 }}>&#x1F9CD;</div>
            <h2 style={{ color: '#C5A46D', fontSize: '1.4rem', marginBottom: '12px', letterSpacing: '2px' }}>
              BIOMETRIC POSE SCANNER
            </h2>
            <p style={{ color: '#999', fontSize: '14px', marginBottom: '30px', maxWidth: '400px', lineHeight: '1.6' }}>
              Real-time body landmark detection using MediaPipe Pose.
              33 keypoints tracked at 30fps for precise garment fitting.
            </p>
            <button
              onClick={startDetection}
              style={{
                padding: '14px 32px',
                backgroundColor: '#C5A46D',
                color: '#141619',
                border: 'none',
                borderRadius: '30px',
                fontWeight: 'bold',
                cursor: 'pointer',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                fontSize: '14px',
                transition: 'transform 0.2s, box-shadow 0.2s',
              }}
              onMouseOver={(e) => {
                e.target.style.transform = 'scale(1.05)';
                e.target.style.boxShadow = '0 4px 20px rgba(197, 164, 109, 0.4)';
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'scale(1)';
                e.target.style.boxShadow = 'none';
              }}
            >
              Activate Pose Detection
            </button>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(20, 22, 25, 0.95)',
              padding: '40px',
              textAlign: 'center',
            }}
          >
            <p style={{ color: '#ff6b6b', fontSize: '14px', marginBottom: '20px' }}>{error}</p>
            <button
              onClick={startDetection}
              style={{
                padding: '10px 24px',
                backgroundColor: '#C5A46D',
                color: '#141619',
                border: 'none',
                borderRadius: '20px',
                fontWeight: 'bold',
                cursor: 'pointer',
              }}
            >
              Retry
            </button>
          </div>
        )}
      </div>

      {/* Measurements Panel */}
      {isDetecting && bodyMeasurements && (
        <div
          style={{
            padding: '16px 20px',
            background: 'linear-gradient(180deg, rgba(20,22,25,0.95), #141619)',
            borderTop: '1px solid rgba(197, 164, 109, 0.2)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ color: '#C5A46D', fontFamily: 'monospace', fontSize: '11px', letterSpacing: '2px' }}>
              BODY PROPORTIONS (NORMALIZED)
            </span>
            <span style={{ color: '#4CAF50', fontFamily: 'monospace', fontSize: '11px' }}>
              ● TRACKING
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
            <MeasurementCard label="Shoulders" value={bodyMeasurements.shoulderWidth} unit="%" />
            <MeasurementCard label="Torso" value={bodyMeasurements.torsoLength} unit="%" />
            <MeasurementCard label="Hips" value={bodyMeasurements.hipWidth} unit="%" />
            <MeasurementCard label="L.Arm" value={bodyMeasurements.leftArm} unit="%" />
            <MeasurementCard label="R.Arm" value={bodyMeasurements.rightArm} unit="%" />
            <MeasurementCard label="S/H Ratio" value={bodyMeasurements.shoulderToHipRatio} unit="" />
          </div>

          {/* Zero-Size Philosophy */}
          <div style={{ marginTop: '12px', padding: '8px 12px', backgroundColor: 'rgba(197, 164, 109, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
            <p style={{ color: '#C5A46D', fontFamily: 'monospace', fontSize: '11px', margin: 0, letterSpacing: '1px' }}>
              ZERO SIZE. ZERO NUMBERS. BIOMETRIC FIT ONLY.
            </p>
          </div>
        </div>
      )}

      {/* Controls */}
      {isDetecting && (
        <div
          style={{
            padding: '12px 20px',
            borderTop: '1px solid rgba(197, 164, 109, 0.15)',
            display: 'flex',
            gap: '10px',
            justifyContent: 'center',
          }}
        >
          <ToggleButton
            label="Skeleton"
            active={showSkeleton}
            onClick={() => setShowSkeleton(!showSkeleton)}
          />
          <ToggleButton
            label="Measurements"
            active={showMeasurements}
            onClick={() => setShowMeasurements(!showMeasurements)}
          />
        </div>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes scan {
          0% { transform: translateY(-100px); opacity: 0.5; }
          50% { transform: translateY(100px); opacity: 1; }
          100% { transform: translateY(-100px); opacity: 0.5; }
        }
      `}</style>
    </div>
  );
}

// ─── SUB-COMPONENTS ──────────────────────────────────────────────────────────

function MeasurementCard({ label, value, unit }) {
  return (
    <div
      style={{
        padding: '8px',
        backgroundColor: 'rgba(255,255,255,0.03)',
        borderRadius: '6px',
        border: '1px solid rgba(197, 164, 109, 0.15)',
        textAlign: 'center',
      }}
    >
      <div style={{ color: '#888', fontSize: '10px', fontFamily: 'monospace', marginBottom: '4px' }}>
        {label}
      </div>
      <div style={{ color: '#F5EFE6', fontSize: '16px', fontWeight: 'bold', fontFamily: 'monospace' }}>
        {value}
        <span style={{ fontSize: '10px', color: '#888' }}>{unit}</span>
      </div>
    </div>
  );
}

function ToggleButton({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '6px 14px',
        backgroundColor: active ? 'rgba(197, 164, 109, 0.2)' : 'transparent',
        color: active ? '#C5A46D' : '#666',
        border: `1px solid ${active ? '#C5A46D' : '#333'}`,
        borderRadius: '16px',
        fontSize: '11px',
        fontFamily: 'monospace',
        cursor: 'pointer',
        transition: 'all 0.2s',
        letterSpacing: '0.5px',
      }}
    >
      {label}
    </button>
  );
}

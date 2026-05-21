import React, { useEffect, useRef, useState } from "react";

interface PauAvatarTalkingProps {
  audioUrl: string;
  isTalking: boolean;
  onFinished: () => void;
}

export const PauAvatarTalking: React.FC<PauAvatarTalkingProps> = ({
  audioUrl,
  isTalking,
  onFinished,
}) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const [mouthOpenScale, setMouthOpenScale] = useState<number>(0);

  useEffect(() => {
    if (!isTalking || !audioUrl) return;

    const audio = new Audio(audioUrl);
    audioRef.current = audio;
    audio.crossOrigin = "anonymous";

    const AudioContextClass =
      window.AudioContext || (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AudioContextClass) return;

    const audioContext = new AudioContextClass();
    audioContextRef.current = audioContext;

    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 256;
    analyserRef.current = analyser;

    const source = audioContext.createMediaElementSource(audio);
    source.connect(analyser);
    analyser.connect(audioContext.destination);

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const cleanup = () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (audioContextRef.current) {
        void audioContextRef.current.close();
        audioContextRef.current = null;
      }
      setMouthOpenScale(0);
    };

    const updateTalkingAnimation = () => {
      if (!analyserRef.current) return;
      analyserRef.current.getByteFrequencyData(dataArray);

      let totalVolume = 0;
      for (let i = 0; i < bufferLength; i += 1) {
        totalVolume += dataArray[i];
      }

      const averageVolume = totalVolume / bufferLength;
      const scale = Math.min(averageVolume / 50, 1.2);
      setMouthOpenScale(scale);

      animationFrameRef.current = requestAnimationFrame(updateTalkingAnimation);
    };

    void audio.play().then(updateTalkingAnimation).catch(console.error);
    audio.onended = () => {
      cleanup();
      onFinished();
    };

    return cleanup;
  }, [isTalking, audioUrl, onFinished]);

  return (
    <div className="pau-coin-container" style={{ position: "relative", width: "120px", height: "120px" }}>
      <img
        src="/assets/pau_moneda_base.png"
        alt="Pau Base"
        style={{ width: "100%", height: "100%", position: "absolute", top: 0, left: 0 }}
      />
      <img
        src="/assets/pau_boca.png"
        alt="Pau Boca"
        style={{
          width: "30px",
          height: "20px",
          position: "absolute",
          top: "65px",
          left: "45px",
          transform: `scaleY(${isTalking ? Math.max(0.2, mouthOpenScale) : 0.1})`,
          transition: "transform 0.05s ease-out",
          transformOrigin: "top center",
        }}
      />
    </div>
  );
};

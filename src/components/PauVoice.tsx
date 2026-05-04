import React from "react";

interface PauVoiceProps {
  message: string;
}

const PauVoice: React.FC<PauVoiceProps> = ({ message }) => (
  <div className="pau-voice">{message}</div>
);

export default PauVoice;

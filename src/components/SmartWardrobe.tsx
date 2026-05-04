import React from "react";

interface SmartWardrobeProps {
  item: string;
  color: string;
}

const SmartWardrobe: React.FC<SmartWardrobeProps> = ({ item, color }) => (
  <div className="smart-wardrobe" style={{ backgroundColor: color }}>
    <span>{item}</span>
  </div>
);

export default SmartWardrobe;

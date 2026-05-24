export type Garment = {
  id: string;
  name: string;
  category: string;
  color: string;
  // Reference garment dimensions used for elastic fit
  dimensions: {
    shoulders: number;
    torso: number;
    hips: number;
    sleeves: number;
  };
};

export type DemoState = "idle" | "loading" | "active" | "error";

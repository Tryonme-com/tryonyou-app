export const STATUS = {
  IDLE: 'idle',
  SCANNING: 'scanning',
  READY: 'ready',
} as const;

export type StatusValue = (typeof STATUS)[keyof typeof STATUS];

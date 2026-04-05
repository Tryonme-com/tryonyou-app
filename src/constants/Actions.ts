export const STATUS = {
  IDLE: 'idle',
  SCANNING: 'scanning',
  READY: 'ready',
  ERROR: 'error',
} as const;

export type StatusValue = (typeof STATUS)[keyof typeof STATUS];

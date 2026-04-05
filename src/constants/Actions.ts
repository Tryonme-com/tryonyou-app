export const ACTIONS = {
  START_SCAN: 'START_SCAN',
  LOCK_IDENTITY: 'LOCK_IDENTITY',
  FINISH: 'FINISH',
} as const;

export type ActionType = typeof ACTIONS[keyof typeof ACTIONS];

export const STATUS = {
  READY: 'READY',
  SCANNING: 'SCANNING',
  LOCKED: 'LOCKED',
  SNAP_READY: 'SNAP_READY',
} as const;

export type StatusType = typeof STATUS[keyof typeof STATUS];

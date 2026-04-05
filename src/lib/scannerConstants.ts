/**
 * Scanner state machine — actions and statuses for the Zero-Size scanning pipeline.
 */

export const ACTIONS = {
  START_SCAN: 'START_SCAN',
  LOCK_IDENTITY: 'LOCK_IDENTITY',
  MESH_LOADED: 'MESH_LOADED',
  FINISH: 'FINISH',
  RESET: 'RESET'
} as const;

export const STATUS = {
  READY: 'READY',
  SCANNING: 'SCANNING',
  LOCKED: 'LOCKED',
  SNAP_READY: 'SNAP_READY'
} as const;

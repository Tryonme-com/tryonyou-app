/**
 * Scanner state machine — actions and status constants (protocolo Zero-Size / biometric scan flow).
 */

export const ACTIONS = {
  START_SCAN: 'START_SCAN',
  LOCK_IDENTITY: 'LOCK_IDENTITY',
  MESH_LOADED: 'MESH_LOADED',
  FINISH: 'FINISH',
  RESET: 'RESET'
};

export const STATUS = {
  READY: 'READY',
  SCANNING: 'SCANNING',
  LOCKED: 'LOCKED',
  SNAP_READY: 'SNAP_READY'
};

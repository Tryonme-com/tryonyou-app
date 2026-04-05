import { useReducer, useCallback } from 'react';
import { ACTIONS, STATUS, IDENTITY } from '../constants/Actions';

const initialState = {
  status: STATUS.READY,
  identity: IDENTITY.LILA_INICIAL,
  patent: typeof import.meta !== 'undefined' && import.meta.env
    ? import.meta.env.VITE_PATENT_ID || 'PCT/EP2025/067317'
    : 'PCT/EP2025/067317'
};

function sovereigntyReducer(state, action) {
  switch (action.type) {
    case ACTIONS.START_SCAN:
      return { ...state, status: STATUS.SCANNING };
    case ACTIONS.LOCK_IDENTITY:
      return { ...state, status: STATUS.LOCKED, identity: action.payload };
    case ACTIONS.MESH_LOADED:
      return { ...state, meshLoaded: true };
    case ACTIONS.FINISH:
      return { ...state, status: STATUS.SNAP_READY };
    case ACTIONS.RESET:
      return { ...initialState };
    default:
      return state;
  }
}

export function useSovereignty() {
  const [state, dispatch] = useReducer(sovereigntyReducer, initialState);

  const startScan = useCallback(() => {
    dispatch({ type: ACTIONS.START_SCAN });
  }, []);

  const lockIdentity = useCallback((colorHex) => {
    dispatch({ type: ACTIONS.LOCK_IDENTITY, payload: colorHex });
  }, []);

  const meshLoaded = useCallback(() => {
    dispatch({ type: ACTIONS.MESH_LOADED });
  }, []);

  const finish = useCallback(() => {
    dispatch({ type: ACTIONS.FINISH });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: ACTIONS.RESET });
  }, []);

  return { state, startScan, lockIdentity, meshLoaded, finish, reset };
}

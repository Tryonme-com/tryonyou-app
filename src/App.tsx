import { useReducer } from "react";
import { DivineMirror } from "./components/DivineMirror";
import { ACTIONS, STATUS, type StatusType } from "./constants/Actions";

interface AppState {
  status: StatusType;
  identity: string;
  patent: string;
}

type AppAction =
  | { type: typeof ACTIONS.START_SCAN }
  | { type: typeof ACTIONS.LOCK_IDENTITY; payload: string }
  | { type: typeof ACTIONS.FINISH };

const initialState: AppState = {
  status: STATUS.READY,
  identity: '#C8A2C8', // Lila Inicial
  patent: (import.meta.env.VITE_PATENT_ID as string | undefined) ?? 'PCT/EP2025/067317',
};

function reducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case ACTIONS.START_SCAN: return { ...state, status: STATUS.SCANNING };
    case ACTIONS.LOCK_IDENTITY: return { ...state, status: STATUS.LOCKED, identity: action.payload };
    case ACTIONS.FINISH: return { ...state, status: STATUS.SNAP_READY };
    default: return state;
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const handleSnapSequence = () => {
    dispatch({ type: ACTIONS.START_SCAN });

    // Simulación de Criba de Datos en us-west1 (2s)
    setTimeout(() => {
      dispatch({ type: ACTIONS.LOCK_IDENTITY, payload: '#E60000' }); // Rojo Valentino
    }, 2000);

    // Finalización: Redirección a Shopify (3.5s)
    setTimeout(() => {
      dispatch({ type: ACTIONS.FINISH });
      console.log("LOGÍSTICA INVISIBLE: REDIRIGIENDO A CHECKOUT...");
    }, 3500);
  };

  return (
    <DivineMirror state={state} onSnap={handleSnapSequence} />
  );
}

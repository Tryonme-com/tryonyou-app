import { motion, AnimatePresence } from 'framer-motion';
import { STATUS, type StatusValue } from '../constants/Actions';

type Props = {
  status: StatusValue;
  identity: string | null;
};

const STATUS_LABELS: Record<StatusValue, string> = {
  [STATUS.IDLE]: 'EN ATTENTE',
  [STATUS.SCANNING]: 'ANALYSE EN COURS',
  [STATUS.READY]: 'SILHOUETTE DÉTECTÉE',
};

export const DivineMirror = ({ status, identity }: Props) => {
  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <AnimatePresence>
        {status === STATUS.SCANNING && (
          <motion.div
            key="scan-line"
            className="mirror-scan"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.55 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        <motion.div
          key={status}
          className="mirror-status"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
        >
          {STATUS_LABELS[status]}
        </motion.div>
      </AnimatePresence>

      <AnimatePresence>
        {status === STATUS.READY && identity && (
          <div
            style={{
              position: 'absolute',
              bottom: 32,
              left: 0,
              right: 0,
              display: 'flex',
              justifyContent: 'center',
              zIndex: 20,
              pointerEvents: 'none',
            }}
          >
            <motion.div
              key="identity"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.45, ease: 'easeOut' }}
              style={{
                fontSize: 11,
                letterSpacing: 3,
                padding: '8px 18px',
                borderRadius: 999,
                border: '1px solid var(--gold)',
                background: 'rgba(0,0,0,0.5)',
                color: 'var(--bone)',
                whiteSpace: 'nowrap',
              }}
            >
              {identity}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

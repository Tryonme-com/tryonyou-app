import { motion, AnimatePresence } from 'framer-motion';
import { STATUS, type StatusValue } from '../constants/Actions';

type Props = {
  status: StatusValue;
  identity?: string | null;
};

const STATUS_LABEL: Record<StatusValue, string> = {
  [STATUS.IDLE]: 'En attente',
  [STATUS.SCANNING]: 'Analyse…',
  [STATUS.READY]: 'Prêt',
  [STATUS.ERROR]: 'Erreur miroir',
};

export const DivineMirror = ({ status, identity }: Props) => {
  const label =
    status === STATUS.READY && identity ? identity : STATUS_LABEL[status];

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
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
          key={label}
          className="mirror-status"
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
          transition={{ duration: 0.3 }}
        >
          {label}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

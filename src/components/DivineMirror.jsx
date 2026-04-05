import { motion, AnimatePresence } from 'framer-motion';
import { STATUS } from '../constants/Actions';

const statusVariants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: { opacity: 1, scale: 1, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, scale: 0.88, transition: { duration: 0.25 } }
};

const pulseVariants = {
  scanning: {
    boxShadow: [
      '0 0 0px 0px rgba(200,162,200,0)',
      '0 0 24px 8px rgba(200,162,200,0.6)',
      '0 0 0px 0px rgba(200,162,200,0)'
    ],
    transition: { duration: 1.4, repeat: Infinity, ease: 'easeInOut' }
  },
  locked: {
    boxShadow: '0 0 32px 12px rgba(230,0,0,0.4)',
    transition: { duration: 0.5 }
  },
  default: {
    boxShadow: '0 0 0px 0px rgba(0,0,0,0)',
    transition: { duration: 0.3 }
  }
};

export const DivineMirror = ({ status, identity }) => {
  const isPulsing = status === STATUS.SCANNING;
  const isLocked = status === STATUS.LOCKED || status === STATUS.SNAP_READY;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 16,
        padding: '24px 0'
      }}
    >
      <motion.div
        animate={isPulsing ? 'scanning' : isLocked ? 'locked' : 'default'}
        variants={pulseVariants}
        style={{
          width: 180,
          height: 240,
          borderRadius: 16,
          background: identity
            ? `linear-gradient(145deg, ${identity}cc 0%, ${identity} 100%)`
            : 'linear-gradient(145deg, #C8A2C8cc 0%, #C8A2C8 100%)',
          border: '1.5px solid rgba(255,255,255,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          position: 'relative'
        }}
      >
        <AnimatePresence mode="wait">
          <motion.span
            key={status}
            variants={statusVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            style={{
              fontSize: 11,
              letterSpacing: 4,
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.85)',
              fontWeight: 600,
              textAlign: 'center',
              padding: '0 12px'
            }}
          >
            {status === STATUS.READY && 'LISTO'}
            {status === STATUS.SCANNING && 'ESCANEANDO…'}
            {status === STATUS.LOCKED && 'IDENTIDAD BLOQUEADA'}
            {status === STATUS.SNAP_READY && 'SNAP LISTO'}
          </motion.span>
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {identity && (
          <motion.p
            key={identity}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0, transition: { duration: 0.35 } }}
            exit={{ opacity: 0, y: -4 }}
            style={{
              fontSize: 10,
              letterSpacing: 3,
              textTransform: 'uppercase',
              color: identity,
              margin: 0,
              fontWeight: 600
            }}
          >
            {identity}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
};

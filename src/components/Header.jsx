const GOLD = '#D4AF37';
const BRANDS = ['BALMAIN', 'CHANEL', 'DIOR', 'YSL'];

/**
 * Header — TRYONME branding bar with luxury brand shortcuts.
 */
export default function Header({ onBrandClick }) {
  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        width: '100%',
        zIndex: 100,
        padding: '30px',
        textAlign: 'center',
        background: 'linear-gradient(to bottom, black, transparent)',
      }}
    >
      <h1 style={{ margin: 0, letterSpacing: 10, fontSize: '1rem', fontWeight: 400 }}>TRYONME</h1>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 20,
          marginTop: 15,
          fontSize: '0.6rem',
          letterSpacing: 3,
          color: GOLD,
        }}
      >
        {BRANDS.map((brand) => (
          <span
            key={brand}
            role="button"
            tabIndex={0}
            style={{ cursor: 'pointer' }}
            onClick={() => onBrandClick && onBrandClick(brand)}
            onKeyDown={(e) => {
              if ((e.key === 'Enter' || e.key === ' ') && onBrandClick) {
                e.preventDefault();
                onBrandClick(brand);
              }
            }}
          >
            {brand}
          </span>
        ))}
      </div>
    </header>
  );
}

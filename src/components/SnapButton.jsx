/**
 * SnapButton — P.A.U. trigger for the Divine Mirror snap action.
 * Calls onSnap when clicked, which triggers the Jules orchestration.
 */
export default function SnapButton({ onSnap }) {
  return (
    <div className="app-pau-row">
      <button
        type="button"
        className="app-pau"
        onClick={onSnap}
        title="P.A.U."
        aria-label="P.A.U. — snap et orchestration Jules"
      >
        <video autoPlay loop muted playsInline preload="auto">
          <source src="/videos/pau_transparent.webm" type="video/webm" />
          <source src="/videos/pau_transparent.mp4" type="video/mp4" />
        </video>
      </button>
    </div>
  );
}

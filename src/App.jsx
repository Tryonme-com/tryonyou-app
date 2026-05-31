// import SmartWardrobe from "./components/Wardrobe/SmartWardrobe";import React from 'react';
import SmartWardrobe from './components/Wardrobe/SmartWardrobe';

function App() {
  return (
    <div className="app-container" style={{ backgroundColor: '#001a2c', color: '#ffffff', minHeight: '100vh' }}>
      <header style={{ padding: '20px', borderBottom: '1px solid #c5a059' }}>
        <h1 style={{ color: '#c5a059', letterSpacing: '1px' }}>TRYONYOU</h1>
      </header>
      <main style={{ padding: '20px' }}>
        <SmartWardrobe />
      </main>
      <footer style={{ textAlign: 'center', padding: '20px', fontSize: '12px', color: '#888888' }}>
        <p>TRYONYOU R&D — Protected under Patent PCT/EP2025/067317</p>
      </footer>
    </div>
  );
}

export default App;

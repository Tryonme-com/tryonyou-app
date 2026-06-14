import React from 'react';
import VirtualMirror from './components/VirtualMirror';

export default function App() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px', fontFamily: 'system-ui, sans-serif' }}>
      <VirtualMirror />
    </div>
  );
}

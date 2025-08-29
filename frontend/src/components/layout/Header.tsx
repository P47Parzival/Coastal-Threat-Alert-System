// src/components/layout/Header.tsx
import React from 'react';
import { ShieldAlert } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="absolute top-0 left-0 right-0 z-10 bg-black/50 backdrop-blur-sm text-white p-4 shadow-lg flex items-center">
      <ShieldAlert className="w-8 h-8 mr-3 text-cyan-400" />
      <h1 className="text-2xl font-bold tracking-wider">Coastal Threat Alert System</h1>
    </header>
  );
};

export default Header;
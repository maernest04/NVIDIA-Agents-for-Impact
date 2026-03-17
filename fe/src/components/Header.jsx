import React from 'react';
import { ShieldAlert, Shield } from 'lucide-react';

const Header = () => {
  return (
    <header className="w-full flex-shrink-0 bg-[#0055A2] border-b-4 border-[#E5A823] shadow-md z-20 relative">
      {/* Emergency Banner */}
      <div className="bg-[#E5A823]/90 py-2.5 px-6 flex items-center justify-center sm:justify-start gap-2 text-[#003d75]">
        <ShieldAlert size={18} className="text-[#003d75] shrink-0 fill-current" />
        <p className="text-sm font-semibold">
          <strong>In immediate danger?</strong> Call 911 or go to the nearest emergency room.
        </p>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center gap-4">
        {/* Spartan Logo Concept */}
        <div className="flex h-12 w-12 bg-white rounded-full items-center justify-center shrink-0 shadow-inner border-2 border-[#E5A823] overflow-hidden">
          <img src="/spartan-avatar.png" alt="Spartan AI" className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight leading-tight m-0 drop-shadow-sm">
            SJSU Safeline
          </h1>
          <p className="text-white/80 text-sm m-0 font-medium">
            Confidential support — campus & national resources when you're not sure where to turn
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header;

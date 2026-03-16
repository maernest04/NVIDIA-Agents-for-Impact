import React, { useState } from 'react';
import { Phone, Clock, Info, Copy, Check, MessageCircleHeart } from 'lucide-react';

const ResourceCard = ({ resource, compact = false }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(resource.callScript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`bg-white w-full rounded-2xl border-2 border-[#0055A2]/10 overflow-hidden shadow-sm hover:shadow-md hover:border-[#0055A2]/30 transition-all group ${compact ? 'mb-2' : 'mb-6'} animate-in slide-in-from-bottom-4 duration-500 fill-mode-both`}>
      {/* Header section */}
      <div className={`${compact ? 'p-4' : 'p-6'} border-b border-slate-100 relative`}>
        <div className="absolute top-0 right-0 w-24 h-24 bg-[#E5A823] opacity-5 rounded-bl-[100px] pointer-events-none"></div>
        <div className="flex justify-between items-start gap-4 position-relative z-10">
          <div>
            <h3 className={`${compact ? 'text-lg' : 'text-xl'} font-bold text-[#0055A2] leading-tight mb-2`}>
              {resource.name}
            </h3>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm font-semibold">
              <span className="flex items-center gap-1.5 text-[#0055A2] bg-[#0055A2]/10 px-2.5 py-1 rounded-md">
                <Phone size={14} />
                {resource.phone}
              </span>
              <span className="flex items-center gap-1.5 text-[#003d75] bg-[#0055A2]/5 px-2.5 py-1 rounded-md">
                <Clock size={14} />
                {resource.availability}
              </span>
            </div>
          </div>
          <a
            href={`tel:${resource.phone.replace(/[^0-9]/g, '')}`}
            className="hidden sm:flex shrink-0 items-center justify-center gap-2 bg-[#0055A2] text-white font-bold px-5 py-2.5 rounded-xl border-b-4 border-[#003d75] hover:bg-[#003d75] active:border-b-0 active:translate-y-1 transition-all"
          >
            <Phone size={16} />
            Call Now
          </a>
        </div>
      </div>

      {/* Body section */}
      <div className={`${compact ? 'p-4' : 'p-6'} bg-slate-50/50 space-y-4`}>
        
        {/* Why it helps */}
        <div className="flex gap-2.5 text-slate-700">
          <div className="shrink-0 mt-0.5 text-[#E5A823]">
            <Info size={18} />
          </div>
          <p className="font-medium text-[15px] leading-relaxed">
            <strong className="text-[#0055A2] font-semibold block mb-0.5">Why this might help:</strong>
            {resource.whyItHelps}
          </p>
        </div>

        {/* Script section */}
        <div className={`bg-white border border-[#E5A823]/30 rounded-xl ${compact ? 'p-4' : 'p-5'} relative overflow-hidden shadow-sm`}>
          <div className="absolute top-0 left-0 w-1.5 h-full bg-[#E5A823] font-medium"></div>
          
          <div className="flex justify-between items-center mb-2 pl-2">
             <span className="flex items-center gap-2 text-xs font-bold tracking-wide text-[#0055A2] uppercase">
               <MessageCircleHeart size={14} />
               What to say when you call
             </span>
             <button
               onClick={handleCopy}
               className="text-xs font-semibold flex items-center gap-1 px-2 py-1 rounded-md text-[#0055A2] hover:bg-[#0055A2]/10 transition-colors"
               aria-label="Copy script"
             >
               {copied ? <Check size={14} className="text-[#E5A823]" strokeWidth={3} /> : <Copy size={14} />}
               {copied ? 'Copied' : 'Copy'}
             </button>
          </div>
          
          <p className={`${compact ? 'text-[15px]' : 'text-[17px]'} text-slate-800 leading-relaxed font-medium italic relative pl-2`}>
            "{resource.callScript}"
          </p>
        </div>

        {/* Mobile Call CTA */}
        <a
          href={`tel:${resource.phone.replace(/[^0-9]/g, '')}`}
          className="sm:hidden w-full flex items-center justify-center gap-2 bg-[#0055A2] text-white font-bold px-5 py-3.5 rounded-xl border-b-4 border-[#003d75] hover:bg-[#003d75] active:border-b-0 active:translate-y-1 transition-all mt-4"
        >
          <Phone size={18} />
          Call {resource.phone}
        </a>
        
      </div>
    </div>
  );
};

export default ResourceCard;

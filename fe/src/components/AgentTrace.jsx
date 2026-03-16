import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Bot, Network, Database } from 'lucide-react';

const AgentTrace = ({ isVisible, status, simulatedCategories }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-4 z-50 w-80 shadow-[0_8px_30px_rgb(0,0,0,0.12)] bg-white rounded-lg border border-slate-200 overflow-hidden font-mono text-xs opacity-90 transition-opacity hover:opacity-100">
      <div 
        className="bg-slate-800 text-[#E5A823] px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-slate-700 transition duration-150"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Terminal size={14} />
          <span className="font-semibold tracking-wider">AGENT.TRACE</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[10px] uppercase">{status}</span>
          {isExpanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-3 bg-slate-50 max-h-64 overflow-y-auto space-y-3">
          
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
              <Bot size={12} />
              <span>ROUTER_AGENT</span>
            </div>
            <div className="pl-4 border-l-2 border-slate-200 text-slate-600">
              {status === 'empty' && "Waiting for user input..."}
              {status === 'loading' && "Parsing intent, classifying urgency..."}
              {status === 'results' && "Classification complete. Routing determined."}
            </div>
          </div>

          {status === 'results' && simulatedCategories && (
             <div className="space-y-1">
               <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
                 <Network size={12} />
                 <span>DETECTED_VECTORS</span>
               </div>
               <div className="pl-4 border-l-2 border-slate-200 flex flex-wrap gap-1">
                 {simulatedCategories.map(cat => (
                   <span key={cat} className="bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded text-[10px]">
                     {cat}
                   </span>
                 ))}
               </div>
             </div>
          )}
          
          {(status === 'loading' || status === 'results') && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
                <Database size={12} />
                <span>RAG_LOOKUP</span>
              </div>
              <div className="pl-4 border-l-2 border-slate-200 text-slate-600">
                {status === 'loading' ? 'Querying resource database...' : 'Returned top matches above confidence threshold 0.85'}
              </div>
            </div>
          )}

        </div>
      )}
    </div>
  );
};

export default AgentTrace;

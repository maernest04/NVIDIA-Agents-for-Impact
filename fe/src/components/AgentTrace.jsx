import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Bot, Network, Database, Zap } from 'lucide-react';

const TOOL_META = {
  assess_urgency:        { label: 'Urgency Assessment',       icon: '⚡', color: 'text-red-600' },
  triage_situation:      { label: 'Situation Triage',         icon: '🔍', color: 'text-yellow-600' },
  search_resources:      { label: 'Resource DB Search',       icon: '🗄️', color: 'text-blue-600' },
  get_resource_by_name:  { label: 'Resource Lookup',          icon: '📋', color: 'text-blue-600' },
  draft_outreach_message:{ label: 'Outreach Draft (Nemotron)', icon: '✍️', color: 'text-teal-600' },
};

const AgentTrace = ({ isVisible, status, agentTrace = { toolCalls: [], categories: [] } }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!isVisible) return null;

  const { toolCalls = [], categories = [] } = agentTrace;
  const hasData = toolCalls.length > 0;

  return (
    <div className="fixed top-20 right-4 z-50 w-80 shadow-[0_8px_30px_rgb(0,0,0,0.12)] bg-white rounded-lg border border-slate-200 overflow-hidden font-mono text-xs opacity-90 transition-opacity hover:opacity-100">
      <div
        className="bg-slate-800 text-[#E5A823] px-3 py-2 flex items-center justify-between cursor-pointer hover:bg-slate-700 transition duration-150"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Terminal size={14} />
          <span className="font-semibold tracking-wider">AGENT.TRACE</span>
          {hasData && (
            <span className="bg-teal-500 text-white text-[9px] px-1.5 py-0.5 rounded-full font-bold">
              LIVE
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <span className="text-[10px] uppercase">{status}</span>
          {isExpanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
        </div>
      </div>

      {isExpanded && (
        <div className="p-3 bg-slate-50 max-h-72 overflow-y-auto space-y-3">

          {/* Agent status */}
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
              <Bot size={12} />
              <span>ROUTER_AGENT</span>
            </div>
            <div className="pl-4 border-l-2 border-slate-200 text-slate-600">
              {status === 'empty'   && 'Waiting for user input...'}
              {status === 'loading' && (
                <span className="flex items-center gap-1">
                  <span className="inline-block w-1.5 h-1.5 bg-yellow-400 rounded-full animate-pulse" />
                  Running tool chain...
                </span>
              )}
              {status === 'results' && 'Routing complete.'}
            </div>
          </div>

          {/* Real tool call steps */}
          {toolCalls.length > 0 && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
                <Zap size={12} />
                <span>REASONING STEPS</span>
              </div>
              <div className="pl-4 border-l-2 border-slate-200 space-y-1.5">
                {toolCalls.map((tool, i) => {
                  const meta = TOOL_META[tool] || { label: tool, icon: '🔧', color: 'text-slate-600' };
                  return (
                    <div key={i} className="flex items-center gap-1.5">
                      <span>{meta.icon}</span>
                      <span className={`${meta.color} font-medium`}>{meta.label}</span>
                      <span className="text-slate-400 ml-auto text-[10px]">✓</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Real Nemotron-identified categories */}
          {categories.length > 0 && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
                <Network size={12} />
                <span>DETECTED VECTORS</span>
              </div>
              <div className="pl-4 border-l-2 border-slate-200 flex flex-wrap gap-1">
                {categories.map(cat => (
                  <span key={cat} className="bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded text-[10px]">
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* RAG lookup status */}
          {(status === 'loading' || status === 'results') && (
            <div className="space-y-1">
              <div className="flex items-center gap-1.5 text-slate-500 font-semibold mb-1">
                <Database size={12} />
                <span>RAG_LOOKUP</span>
              </div>
              <div className="pl-4 border-l-2 border-slate-200 text-slate-600">
                {status === 'loading'
                  ? 'Querying resource database...'
                  : 'Returned top matches above confidence threshold'}
              </div>
            </div>
          )}

          {!hasData && status === 'empty' && (
            <p className="text-slate-400 text-center py-2">No trace yet — send a message.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentTrace;

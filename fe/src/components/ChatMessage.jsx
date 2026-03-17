import React from 'react';
import { User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import ResourceCard from './ResourceCard';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-8 animate-in slide-in-from-bottom-2 duration-300 fill-mode-both`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-3`}>
        
        {/* Avatar */}
        <div className={`shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm border-2 mt-1 ${
          isUser 
            ? 'bg-[#0055A2] text-white border-[#003d75] ml-2' 
            : 'bg-white text-[#0055A2] border-[#E5A823] mr-2 overflow-hidden'
        }`}>
          {isUser ? <User size={18} /> : <img src="/spartan-avatar.png" alt="AI" className="w-full h-full object-cover" />}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col gap-3 w-full ${isUser ? 'items-end' : 'items-start'}`}>
          
          {/* Sender Label */}
          {!isUser && (
            <span className="text-xs font-bold text-[#0055A2] uppercase tracking-wider ml-1">Spartan AI</span>
          )}

          {message.text && (
            <div className={`px-5 py-3.5 rounded-2xl md:text-[16px] leading-relaxed shadow-sm font-medium ${
              isUser 
                ? 'bg-[#0055A2] text-white rounded-br-sm' 
                : 'bg-white border border-slate-100 text-slate-800 rounded-bl-sm'
            }`}>
              {isUser ? (
                message.text
              ) : (
                <ReactMarkdown
                  components={{
                    p:      ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    strong: ({ children }) => <strong className="font-bold text-[#0055A2]">{children}</strong>,
                    em:     ({ children }) => <em className="italic">{children}</em>,
                    ul:     ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
                    ol:     ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
                    li:     ({ children }) => <li className="leading-relaxed">{children}</li>,
                  }}
                >
                  {message.text}
                </ReactMarkdown>
              )}
              {/* Blinking cursor while streaming */}
              {message.isStreaming && (
                <span className="inline-block w-[2px] h-[1.1em] bg-[#0055A2] ml-1 animate-pulse align-text-bottom"></span>
              )}
            </div>
          )}

          {/* Render Attached Resources AFTER streaming finishes */}
          {message.showResources && message.resources && message.resources.length > 0 && (
            <div className="flex flex-col gap-4 mt-2 w-full max-w-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              {message.resources.map((resource, index) => (
                <div key={resource.id} className="animate-in slide-in-from-bottom-4 duration-500" style={{ animationDelay: `${index * 200}ms`, animationFillMode: 'both' }}>
                  <ResourceCard resource={resource} compact />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;

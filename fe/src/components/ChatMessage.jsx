import React from 'react';
import { User, ShieldCheck } from 'lucide-react';
import ResourceCard from './ResourceCard';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-8 animate-in slide-in-from-bottom-2 duration-300 fill-mode-both`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-3`}>
        
        {/* Avatar */}
        <div className={`shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm border-2 ${
          isUser 
            ? 'bg-[#0055A2] text-white border-[#003d75] ml-2' 
            : 'bg-white text-[#0055A2] border-[#E5A823] mr-2'
        }`}>
          {isUser ? <User size={18} /> : <ShieldCheck size={20} className="fill-[#0055A2]/10" />}
        </div>

        {/* Message Content Bubble */}
        <div className={`flex flex-col gap-3 w-full ${isUser ? 'items-end' : 'items-start'}`}>
          {message.text && (
            <div className={`px-5 py-3.5 rounded-2xl md:text-[16px] leading-relaxed shadow-sm font-medium ${
              isUser 
                ? 'bg-[#0055A2] text-white rounded-br-sm' 
                : 'bg-white border border-slate-100 text-slate-800 rounded-bl-sm'
            }`}>
              {message.text}
            </div>
          )}

          {/* Render Attached Resources in the Chat Flow */}
          {message.resources && message.resources.length > 0 && (
            <div className="flex flex-col gap-4 mt-2 w-full max-w-xl">
              {message.resources.map(resource => (
                <ResourceCard key={resource.id} resource={resource} compact />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;

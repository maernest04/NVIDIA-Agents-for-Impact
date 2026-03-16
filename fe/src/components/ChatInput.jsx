import React, { useState, useEffect, useRef } from 'react';
import { Send, Sparkles } from 'lucide-react';

const ChatInput = ({ onSendMessage, isTyping }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isTyping) {
        onSendMessage(input.trim());
        setInput('');
      }
    }
  };

  const handleSend = () => {
    if (input.trim() && !isTyping) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="border-t border-slate-200 bg-white p-4">
      <div className="max-w-3xl mx-auto relative rounded-3xl border-2 border-slate-200 focus-within:border-[#E5A823] focus-within:shadow-md transition-all duration-300 bg-white flex items-end overflow-hidden p-1 group">
        
        {/* Decorative background glow that activates on focus */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-[rgba(0,85,162,0.05)] to-[rgba(229,168,35,0.08)] opacity-0 group-focus-within:opacity-100 transition-opacity duration-500"></div>

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message SJSU Support..."
          disabled={isTyping}
          className="flex-1 max-h-[120px] resize-none bg-transparent p-3 pl-4 pr-12 outline-none text-[#0055A2] font-medium placeholder-[#939597]"
          rows={1}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isTyping}
          className={`absolute right-2 bottom-2 p-2 rounded-full transition-all duration-200 flex items-center justify-center ${
            input.trim() && !isTyping
              ? 'bg-[#0055A2] text-white hover:bg-[#003d75] shadow-sm transform hover:scale-105'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          <Send size={18} />
        </button>
      </div>
      <div className="text-center mt-3 text-xs text-[#939597] font-medium flex items-center justify-center gap-1.5">
        <Sparkles size={12} className="text-[#E5A823]" />
        Private, non-judgmental, and secure chat.
      </div>
    </div>
  );
};

export default ChatInput;

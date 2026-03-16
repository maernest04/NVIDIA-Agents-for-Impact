import React, { useRef, useEffect } from 'react';
import Header from './Header';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import AgentTrace from './AgentTrace';
import { Loader2 } from 'lucide-react';

const ChatLayout = ({ messages, isTyping, onSendMessage, status, simulatedCategories }) => {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages, isTyping]);

  return (
    <div className="flex flex-col h-[100dvh] bg-slate-50 overflow-hidden">
      <Header />
      
      {/* Scrollable Message Area */}
      <main className="flex-1 overflow-y-auto px-4 py-8" ref={scrollRef}>
        <div className="max-w-3xl mx-auto flex flex-col w-full h-full">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center opacity-70 animate-in fade-in h-full my-auto mt-20">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center border-4 border-[#E5A823] shadow-md mb-6">
                 <img 
                   src="https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/San_Jose_State_Spartans_logo.svg/300px-San_Jose_State_Spartans_logo.svg.png" 
                   alt="SJSU Spartan" 
                   className="w-12 h-12 object-contain"
                   onError={(e) => {
                     e.currentTarget.style.display = 'none';
                     e.currentTarget.parentElement.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[#0055A2]"><path d="m12 14 4-4"/><path d="M3.3 7H6"/><path d="m8 18 4-4"/><path d="M2.6 15.1c5.5-.3 8.5 2.5 11 5.9.8.9 2-.2 2.7-.9l.8-.8c1-1 3.5-.8 5-.4M21.4 8.9c-5.5.3-8.5-2.5-11-5.9-.8-.9-2 .2-2.7.9l-.8.8c-1 1-3.5.8-5 .4"/><path d="M14.6 17.6c-5.5.3-8.5-2.5-11-5.9-.8-.9-2 .2-2.7-.9l-.8-.8c1-1 3.5-.8 5-.4"/></svg>';
                   }}
                 />
              </div>
              <h2 className="text-2xl font-bold text-[#0055A2] mb-3">How can we support you today?</h2>
              <p className="text-[#939597] font-medium max-w-md">
                Describe your situation below. We'll connect you directly to confidential resources, local services, and call scripts.
              </p>
            </div>
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}

          {isTyping && (
            <div className="flex w-full justify-start mb-8 animate-in slide-in-from-bottom-2">
              <div className="flex max-w-[85%] flex-row items-end gap-3">
                <div className="shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm border-2 bg-white text-[#0055A2] border-[#E5A823] mr-2">
                  <Loader2 size={20} className="animate-spin" />
                </div>
                <div className="px-5 py-3.5 bg-white border border-slate-100 rounded-2xl rounded-bl-sm flex items-center gap-1.5 h-[52px]">
                   <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                   <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                   <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <ChatInput onSendMessage={onSendMessage} isTyping={isTyping} />
      
      <AgentTrace 
        isVisible={true} 
        status={status} 
        simulatedCategories={simulatedCategories}
      />
    </div>
  );
};

export default ChatLayout;

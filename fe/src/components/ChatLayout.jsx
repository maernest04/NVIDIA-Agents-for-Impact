import React, { useRef, useEffect } from 'react';
import Header from './Header';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import AgentTrace from './AgentTrace';

const ChatLayout = ({ messages, thinkingState, onSendMessage, status, agentTrace }) => {
  const scrollRef = useRef(null);

  // Auto-scroll to bottom on new messages or streaming updates
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages, thinkingState]);

  return (
    <div className="flex flex-col h-[100dvh] bg-slate-50 overflow-hidden">
      <Header />
      
      {/* Scrollable Message Area */}
      <main className="flex-1 overflow-y-auto px-4 py-8" ref={scrollRef}>
        <div className="max-w-3xl mx-auto flex flex-col w-full h-full">
          {messages.length === 0 && !thinkingState ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center animate-in fade-in h-full my-auto mt-20">
              <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center border-4 border-[#E5A823] shadow-md mb-6 overflow-hidden">
                 <img 
                   src="/spartan-avatar.png" 
                   alt="SJSU Spartan AI" 
                   className="w-full h-full object-cover"
                 />
              </div>
              <h2 className="text-2xl font-bold text-[#0055A2] mb-3">How can we support you today?</h2>
              <p className="text-[#939597] font-medium max-w-md mb-8">
                No judgment — many students feel nervous reaching out. Describe your situation in your own words. We'll match you to the right campus or national resource and give you a message you can send or say.
              </p>

              {/* Suggestion Chips */}
              <div className="flex flex-wrap gap-2 max-w-lg justify-center">
                {["I'm feeling overwhelmed", "I don't feel safe at home", "I need mental health support", "I'm worried about a friend"].map((chip) => (
                  <button
                    key={chip}
                    onClick={() => onSendMessage(chip)}
                    className="text-sm bg-white border border-slate-200 text-[#0055A2] font-medium rounded-full px-4 py-2 hover:bg-[#0055A2] hover:text-white hover:border-[#0055A2] transition-colors duration-200 shadow-sm"
                  >
                    {chip}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
          )}

          {/* Thinking Indicator — shown before streaming starts */}
          {thinkingState === 'thinking' && (
            <div className="flex w-full justify-start mb-8 animate-in slide-in-from-bottom-2">
              <div className="flex flex-row items-start gap-3">
                <div className="shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center shadow-sm border-2 bg-white text-[#0055A2] border-[#E5A823] mr-2 overflow-hidden mt-1">
                  <img src="/spartan-avatar.png" alt="Thinking" className="w-full h-full object-cover" />
                </div>
                <div className="flex flex-col gap-2">
                  <span className="text-xs font-bold text-[#0055A2] uppercase tracking-wider ml-1">Spartan AI</span>
                  <div className="px-5 py-3.5 bg-white border border-slate-100 rounded-2xl rounded-bl-sm flex items-center gap-2 shadow-sm">
                    <div className="flex gap-1.5 items-center">
                      <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-[#0055A2] rounded-full animate-bounce"></div>
                    </div>
                    <span className="text-sm text-[#939597] font-medium ml-2">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      <ChatInput onSendMessage={onSendMessage} isTyping={!!thinkingState} />
      
      <AgentTrace
        isVisible={true}
        status={status}
        agentTrace={agentTrace}
      />
    </div>
  );
};

export default ChatLayout;

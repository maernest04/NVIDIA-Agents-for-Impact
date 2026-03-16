import React, { useState, useCallback } from 'react';
import ChatLayout from './components/ChatLayout';
import { mockResources, mockCategories } from './data/mockData';

const generateId = () => Math.random().toString(36).substring(2, 9);

// Varied AI responses to feel more natural across turns
const aiResponses = [
  "I hear you, and I want you to know that reaching out takes real courage. Based on what you've shared, I've found these confidential support options that are best equipped to help you right now. You don't have to face this alone.",
  "Thank you for trusting me with this. I've identified some resources that can provide immediate, confidential support for what you're going through. Here's what I found:",
  "I understand this is difficult, and I'm glad you reached out. I've matched you with these support services — each one is free, confidential, and available right now:",
  "You're not alone in this, and it's okay to ask for help. Based on what you've described, here are the best resources I can connect you with:",
];

function App() {
  const [messages, setMessages] = useState([]);
  const [thinkingState, setThinkingState] = useState(null); // null | 'thinking' | 'streaming'
  const [status, setStatus] = useState('empty');
  const [simulatedCategories, setSimulatedCategories] = useState([]);
  const [responseCount, setResponseCount] = useState(0);

  const handleSendMessage = useCallback((text) => {
    // 1. Add User Message
    const userMessage = {
      id: generateId(),
      role: 'user',
      text: text,
    };
    
    setMessages(prev => [...prev, userMessage]);
    setThinkingState('thinking');
    setStatus('loading');

    // 2. Simulate "Thinking..." phase (1.5s)
    setTimeout(() => {
      // Pick random simulated categories for AgentTrace
      const mockDetected = mockCategories
        .sort(() => 0.5 - Math.random())
        .slice(0, 2)
        .map(c => c.id);
      setSimulatedCategories(mockDetected);

      // 3. Switch to streaming phase — add the message shell first (empty text)
      const responseText = aiResponses[responseCount % aiResponses.length];
      const assistantMessage = {
        id: generateId(),
        role: 'assistant',
        text: '', // starts empty, will be streamed
        fullText: responseText,
        resources: mockResources,
        isStreaming: true,
        showResources: false,
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setThinkingState('streaming');
      setResponseCount(prev => prev + 1);

      // 4. Stream in words one by one
      const words = responseText.split(' ');
      let wordIndex = 0;

      const streamInterval = setInterval(() => {
        wordIndex++;
        if (wordIndex <= words.length) {
          const partialText = words.slice(0, wordIndex).join(' ');
          setMessages(prev => prev.map(msg => 
            msg.id === assistantMessage.id 
              ? { ...msg, text: partialText }
              : msg
          ));
        } else {
          // Done streaming text — now reveal resource cards
          clearInterval(streamInterval);
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessage.id
              ? { ...msg, isStreaming: false, showResources: true }
              : msg
          ));
          setThinkingState(null);
          setStatus('results');
        }
      }, 45); // ~45ms per word for natural speed

    }, 1800); // 1.8 second "thinking" delay
  }, [responseCount]);

  return (
    <div className="selection:bg-[#E5A823]/30 selection:text-[#0055A2]">
      <ChatLayout 
        messages={messages}
        thinkingState={thinkingState}
        onSendMessage={handleSendMessage}
        status={status}
        simulatedCategories={simulatedCategories}
      />
    </div>
  );
}

export default App;

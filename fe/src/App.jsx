import React, { useState, useCallback } from 'react';
import ChatLayout from './components/ChatLayout';
import { mockCategories } from './data/mockData';

const generateId = () => Math.random().toString(36).substring(2, 9);

function App() {
  const [messages, setMessages] = useState([]);
  const [thinkingState, setThinkingState] = useState(null); // null | 'thinking' | 'streaming'
  const [status, setStatus] = useState('empty');
  const [simulatedCategories, setSimulatedCategories] = useState([]);

  const handleSendMessage = useCallback(async (text) => {
    // 1. Add user message immediately
    const userMessage = { id: generateId(), role: 'user', text };
    setMessages(prev => [...prev, userMessage]);
    setThinkingState('thinking');
    setStatus('loading');

    // Simulate category detection in the AgentTrace while waiting
    const mockDetected = mockCategories
      .sort(() => 0.5 - Math.random())
      .slice(0, 2)
      .map(c => c.id);
    setSimulatedCategories(mockDetected);

    try {
      // 2. Call the real backend
      const res = await fetch('/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      const responseText = data.response ?? '';
      const resources = data.resources ?? [];

      // 3. Add assistant message shell (empty), switch to streaming phase
      const assistantId = generateId();
      setMessages(prev => [...prev, {
        id: assistantId,
        role: 'assistant',
        text: '',
        fullText: responseText,
        resources,
        isStreaming: true,
        showResources: false,
      }]);
      setThinkingState('streaming');

      // 4. Stream words one by one for natural feel
      const words = responseText.split(' ');
      let wordIndex = 0;

      const streamInterval = setInterval(() => {
        wordIndex++;
        if (wordIndex <= words.length) {
          setMessages(prev => prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, text: words.slice(0, wordIndex).join(' ') }
              : msg
          ));
        } else {
          clearInterval(streamInterval);
          setMessages(prev => prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, isStreaming: false, showResources: true }
              : msg
          ));
          setThinkingState(null);
          setStatus('results');
        }
      }, 45);

    } catch (err) {
      // Show error as an assistant message so the UI doesn't get stuck
      setMessages(prev => [...prev, {
        id: generateId(),
        role: 'assistant',
        text: `Sorry, something went wrong: ${err.message}. Please try again.`,
        resources: [],
        isStreaming: false,
        showResources: false,
      }]);
      setThinkingState(null);
      setStatus('empty');
    }
  }, []);

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

import React, { useState, useCallback } from 'react';
import ChatLayout from './components/ChatLayout';
<<<<<<< HEAD
=======
import { sendChatMessage } from './api';
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
import { mockCategories } from './data/mockData';

const generateId = () => Math.random().toString(36).substring(2, 9);

function App() {
  const [messages, setMessages] = useState([]);
  const [thinkingState, setThinkingState] = useState(null); // null | 'thinking' | 'streaming'
  const [status, setStatus] = useState('empty');
  const [simulatedCategories, setSimulatedCategories] = useState([]);
<<<<<<< HEAD

  const handleSendMessage = useCallback(async (text) => {
    // 1. Add user message immediately
    const userMessage = { id: generateId(), role: 'user', text };
=======
  const [error, setError] = useState(null);

  const handleSendMessage = useCallback(async (text) => {
    setError(null);

    // 1. Add User Message
    const userMessage = {
      id: generateId(),
      role: 'user',
      text: text,
    };
    
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
    setMessages(prev => [...prev, userMessage]);
    setThinkingState('thinking');
    setStatus('loading');

<<<<<<< HEAD
    // Simulate category detection in the AgentTrace while waiting
=======
    // Simulate category detection for the AgentTrace panel
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
    const mockDetected = mockCategories
      .sort(() => 0.5 - Math.random())
      .slice(0, 2)
      .map(c => c.id);
    setSimulatedCategories(mockDetected);

    try {
<<<<<<< HEAD
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
=======
      // 2. Build conversation history from completed messages (exclude streaming)
      // We read from the current messages state + the new user message
      const currentMessages = [...messages, userMessage];
      const history = currentMessages
        .filter(m => !m.isStreaming && m.text) // only completed messages with text
        .map(m => ({ role: m.role, content: m.role === 'user' ? m.text : (m.fullText || m.text) }));
      
      // Remove the last entry (current message) since it goes as `message` param
      history.pop();

      // 3. Call the real backend with history
      const aiResponseText = await sendChatMessage(text, history);

      // 3. Stream the response word-by-word
      const assistantMessageId = generateId();
      const assistantMessage = {
        id: assistantMessageId,
        role: 'assistant',
        text: '',
        fullText: aiResponseText,
        isStreaming: true,
        showResources: false,
        resources: [],
      };

      setMessages(prev => [...prev, assistantMessage]);
      setThinkingState('streaming');

      // Stream words in
      const words = aiResponseText.split(' ');
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
      let wordIndex = 0;

      const streamInterval = setInterval(() => {
        wordIndex++;
        if (wordIndex <= words.length) {
<<<<<<< HEAD
          setMessages(prev => prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, text: words.slice(0, wordIndex).join(' ') }
=======
          const partialText = words.slice(0, wordIndex).join(' ');
          setMessages(prev => prev.map(msg =>
            msg.id === assistantMessageId
              ? { ...msg, text: partialText }
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
              : msg
          ));
        } else {
          clearInterval(streamInterval);
          setMessages(prev => prev.map(msg =>
<<<<<<< HEAD
            msg.id === assistantId
              ? { ...msg, isStreaming: false, showResources: true }
=======
            msg.id === assistantMessageId
              ? { ...msg, isStreaming: false }
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
              : msg
          ));
          setThinkingState(null);
          setStatus('results');
        }
<<<<<<< HEAD
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
=======
      }, 30); // ~30ms per word for fast but visible streaming

    } catch (err) {
      // Handle errors gracefully
      console.error('Chat API error:', err);
      setError(err.message);
      
      const errorMessage = {
        id: generateId(),
        role: 'assistant',
        text: `I'm sorry, I wasn't able to connect to the support system right now. Please try again in a moment, or if you need immediate help, call **988** (Suicide & Crisis Lifeline) or **911** for emergencies.\n\nError: ${err.message}`,
        isStreaming: false,
        showResources: false,
        resources: [],
      };
      setMessages(prev => [...prev, errorMessage]);
>>>>>>> cd8999264621a378b689b5a45bd1f0dffd6dd23c
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

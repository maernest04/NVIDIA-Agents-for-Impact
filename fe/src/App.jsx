import React, { useState } from 'react';
import ChatLayout from './components/ChatLayout';
import { mockResources, mockCategories } from './data/mockData';

const generateId = () => Math.random().toString(36).substring(2, 9);

function App() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [status, setStatus] = useState('empty'); // for AgentTrace panel only
  const [simulatedCategories, setSimulatedCategories] = useState([]);

  const handleSendMessage = (text) => {
    // 1. Add User Message
    const userMessage = {
      id: generateId(),
      role: 'user',
      text: text
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setStatus('loading');

    // 2. Simulate Backend / Agent routing logic
    setTimeout(() => {
      // Pick random simulated categories
      const mockDetected = mockCategories
        .sort(() => 0.5 - Math.random())
        .slice(0, 2)
        .map(c => c.id);
        
      setSimulatedCategories(mockDetected);
      
      // 3. Add AI Assistant Message with resources attached
      const assistantMessage = {
        id: generateId(),
        role: 'assistant',
        text: "I understand. Based on what you shared, I've found these confidential support options that are best equipped to help you right now. You don't have to face this alone.",
        resources: mockResources // Using all mocked ones for the demo
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
      setStatus('results');
    }, 2500); // 2.5 second simulated wait
  };

  return (
    <div className="selection:bg-[#E5A823]/30 selection:text-[#0055A2]">
      <ChatLayout 
        messages={messages}
        isTyping={isTyping}
        onSendMessage={handleSendMessage}
        status={status}
        simulatedCategories={simulatedCategories}
      />
    </div>
  );
}

export default App;

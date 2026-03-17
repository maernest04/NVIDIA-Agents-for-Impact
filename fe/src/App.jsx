import React, { useState, useCallback, useRef, useEffect } from 'react';
import ChatLayout from './components/ChatLayout';
import { sendChatMessage } from './api';

const generateId = () => Math.random().toString(36).substring(2, 9);

function App() {
  const [messages, setMessages] = useState([]);
  const [thinkingState, setThinkingState] = useState(null); // null | 'thinking' | 'streaming'
  const [status, setStatus] = useState('empty');
  const [agentTrace, setAgentTrace] = useState({ toolCalls: [], categories: [] });

  // Ref keeps handleSendMessage's closure from going stale while still reading
  // the latest messages for building conversation history.
  const messagesRef = useRef([]);
  useEffect(() => { messagesRef.current = messages; }, [messages]);

  const handleSendMessage = useCallback(async (text) => {
    const userMessage = { id: generateId(), role: 'user', text };
    setMessages(prev => [...prev, userMessage]);
    setThinkingState('thinking');
    setStatus('loading');
    setAgentTrace({ toolCalls: [], categories: [] });

    // Build history from all completed (non-streaming) messages before this one
    const history = messagesRef.current
      .filter(m => !m.isStreaming && (m.text || m.fullText))
      .map(m => ({ role: m.role, content: m.fullText || m.text }));

    const assistantId = generateId();
    // Don't add assistant message yet — only show "Thinking..." until first token

    const liveToolCalls = [];
    let liveCategories = [];
    let liveText = '';
    let assistantInList = false;

    try {
      await sendChatMessage(text, history, (event) => {
        if (event.type === 'tool_call') {
          liveToolCalls.push(event.tool);
          setAgentTrace({ toolCalls: [...liveToolCalls], categories: liveCategories });

        } else if (event.type === 'categories') {
          liveCategories = event.categories;
          setAgentTrace({ toolCalls: [...liveToolCalls], categories: liveCategories });

        } else if (event.type === 'token') {
          liveText += event.content;
          setThinkingState('streaming');
          if (!assistantInList) {
            assistantInList = true;
            setMessages(prev => [...prev, {
              id: assistantId,
              role: 'assistant',
              text: liveText,
              fullText: liveText,
              isStreaming: true,
              resources: [],
            }]);
          } else {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantId
                ? { ...msg, text: liveText, fullText: liveText }
                : msg
            ));
          }

        } else if (event.type === 'done') {
          if (!assistantInList) {
            setMessages(prev => [...prev, {
              id: assistantId,
              role: 'assistant',
              text: liveText,
              fullText: liveText,
              isStreaming: false,
              resources: [],
            }]);
          } else {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantId ? { ...msg, isStreaming: false } : msg
            ));
          }
          setThinkingState(null);
          setStatus('results');

        } else if (event.type === 'error') {
          throw new Error(event.message);
        }
      });
    } catch (err) {
      console.error('Chat error:', err);
      const errorText = `I'm sorry, I wasn't able to connect right now. If you need immediate help, call **988** (Suicide & Crisis Lifeline) or **911** for emergencies.\n\nError: ${err.message}`;
      setMessages(prev => {
        if (assistantInList) {
          return prev.map(msg =>
            msg.id === assistantId
              ? { ...msg, text: errorText, fullText: '', isStreaming: false }
              : msg
          );
        }
        return [...prev, {
          id: assistantId,
          role: 'assistant',
          text: errorText,
          fullText: '',
          isStreaming: false,
          resources: [],
        }];
      });
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
        agentTrace={agentTrace}
      />
    </div>
  );
}

export default App;

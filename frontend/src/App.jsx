import { useState, useRef, useEffect } from 'react'
import './index.css'

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'System Online. BusinessOps AI ready. All 8 enterprise integrations (PostgreSQL, Salesforce, Workspace, Slack, Jira, Notion, Pinecone, Power BI) are loaded. How can I assist you today?' }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);

    // Real API call to ADK Backend using strict ADK protocol
    const fetchResponse = async () => {
      try {
        // Step 1: Create a session (Required by ADK)
        const sessionRes = await fetch('/adk-api/apps/app/users/test-user/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        
        if (!sessionRes.ok) {
          throw new Error(`Session creation failed: ${sessionRes.status}`);
        }
        const sessionData = await sessionRes.json();
        const sessionId = sessionData.id;

        // Step 2: Send the message using the exact ADK schema
        const runRes = await fetch('/adk-api/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            app_name: 'app',
            user_id: 'test-user',
            session_id: sessionId,
            new_message: { role: 'user', parts: [{ text: input }] }
          })
        });

        if (!runRes.ok) {
          throw new Error(`Run execution failed: ${runRes.status}`);
        }

        const data = await runRes.json();
        
        // Extract the final agent message from the returned state
        let replyText = "Success, but could not parse text from payload.";
        if (data.messages && data.messages.length > 0) {
            const lastMsg = data.messages[data.messages.length - 1];
            if (lastMsg.parts && lastMsg.parts.length > 0) {
                replyText = lastMsg.parts[0].text;
            }
        } else if (data.text) {
            replyText = data.text; // Fallback
        }

        setMessages([...newMessages, { role: 'assistant', text: replyText }]);
      } catch (error) {
        setMessages([...newMessages, { 
          role: 'assistant', 
          text: `[CONNECTION ERROR]\n\nFailed to reach the ADK Backend at localhost:8000. \n\nDetails: ${error.message}\n\nPlease ensure 'uv run adk web app' is running in a separate terminal window.` 
        }]);
      } finally {
        setIsTyping(false);
      }
    };

    fetchResponse();
  };

  return (
    <div className="container">
      
      {/* Header */}
      <header className="glass-panel header">
        <div>
          <h1 className="title neon-text-sky">BusinessOps <span className="neon-text-navy">AI</span></h1>
          <p className="subtitle">Enterprise Orchestration Node</p>
        </div>
        <div className="status-indicator">
          <div className="dot"></div>
          <span className="status-text">SYSTEM SECURE</span>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="glass-panel main-chat">
        <div className="chat-history">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className={`message-bubble ${msg.role}`}>
                <div className="message-role">
                  {msg.role === 'user' ? 'Operator' : 'AI Agent'}
                </div>
                <div className="message-text">
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-wrapper assistant">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter operational directive..."
              className="chat-input"
            />
            <button 
              type="submit"
              disabled={!input.trim()}
              className="submit-btn"
            >
              EXECUTE
            </button>
          </form>
        </div>
      </main>

    </div>
  )
}

export default App

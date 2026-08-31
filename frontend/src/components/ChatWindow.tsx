import React, { useState } from 'react';
import { useChat } from '../hooks/useChat';

export const ChatWindow: React.FC = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    sendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4 bg-slate-900 text-slate-100">
      <header className="py-4 border-b border-slate-800 flex justify-between items-center">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          DocuMindAI — Document Intelligence
        </h1>
        <span className="text-xs px-2 py-1 bg-blue-950 text-blue-300 border border-blue-800 rounded">
          FastAPI + ChromaDB + RAG
        </span>
      </header>

      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {messages.map((m) => (
          <div key={m.id} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-4 rounded-xl max-w-2xl ${m.role === 'user' ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'}`}>
              <p className="text-sm whitespace-pre-wrap">{m.content}</p>
              
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-2 border-t border-slate-700">
                  <span className="text-xs font-semibold text-slate-400">Sources:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {m.citations.map((c, idx) => (
                      <span key={idx} className="text-xs bg-slate-900 text-blue-300 px-2 py-1 rounded border border-slate-700">
                        📄 {c.document_name} (p. {c.page_number}) • {Math.round(c.score * 100)}%
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSend} className="pt-4 border-t border-slate-800 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your uploaded documents..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-lg text-sm font-medium transition disabled:opacity-50"
        >
          {isLoading ? 'Thinking...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

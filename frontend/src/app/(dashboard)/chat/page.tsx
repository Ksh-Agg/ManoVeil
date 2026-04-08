'use client';

import { useEffect, useRef, useState } from 'react';
import { apiFetch } from '@/lib/api-client';
import { useAuthStore } from '@/stores/auth-store';
import { PERSONAS } from '@/lib/constants';

interface Message { id: string; role: string; content: string; crisis_flag: boolean; created_at: string; }

export default function ChatPage() {
  const { user } = useAuthStore();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [crisisAlert, setCrisisAlert] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const persona = user?.persona as keyof typeof PERSONAS || 'manoveil_core';
  const personaInfo = PERSONAS[persona] || PERSONAS.manoveil_core;

  useEffect(() => {
    apiFetch<any>('/api/v1/chat/sessions', { method: 'POST' })
      .then((s) => setSessionId(s.id))
      .catch(() => {});
  }, []);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const send = async () => {
    if (!input.trim() || !sessionId || loading) return;
    const text = input;
    setInput('');
    setLoading(true);

    try {
      const res = await apiFetch<any>(`/api/v1/chat/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content: text }),
      });
      setMessages((prev) => [...prev, res.user_message, res.bot_message]);
      if (res.crisis_detected) setCrisisAlert(true);
    } catch (err) {
      setMessages((prev) => [...prev, { id: 'err', role: 'assistant', content: 'Sorry, something went wrong. Please try again.', crisis_flag: false, created_at: new Date().toISOString() }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Chat with {personaInfo.name}</h2>

      {/* Crisis Banner */}
      {crisisAlert && (
        <div className="mb-4 p-4 bg-red-50 border-2 border-red-200 rounded-2xl">
          <p className="text-red-800 font-semibold">We&apos;re here for you. If you need immediate help:</p>
          <p className="text-red-700 text-sm mt-1">Kiran Mental Health: <strong>1800-599-0019</strong> (24/7, toll-free)</p>
          <button onClick={() => setCrisisAlert(false)} className="mt-2 text-xs text-red-500 hover:underline">Dismiss</button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 py-20">
            <p className="text-5xl mb-4">💬</p>
            <p>Start a conversation with {personaInfo.name}</p>
            <p className="text-sm mt-2">Your companion is here to listen and support you.</p>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed ${
              m.role === 'user'
                ? 'bg-emerald-600 text-white rounded-br-sm'
                : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-sm'
            }`}>
              {m.content.split('\n').map((line, i) => <p key={i} className={i > 0 ? 'mt-2' : ''}>{line}</p>)}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl rounded-bl-sm border border-gray-100 shadow-sm text-gray-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3 pt-4 border-t">
        <input type="text" value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="Type your message..."
          className="flex-1 px-5 py-3 rounded-2xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
        <button onClick={send} disabled={loading || !input.trim()}
          className="px-6 py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition disabled:opacity-50 font-medium">
          Send
        </button>
      </div>
    </div>
  );
}

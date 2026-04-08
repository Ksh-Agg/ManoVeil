'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';
import { MOOD_EMOJIS } from '@/lib/constants';

export default function MoodTrackerPage() {
  const [selected, setSelected] = useState<string | null>(null);
  const [note, setNote] = useState('');
  const [history, setHistory] = useState<any[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiFetch<any[]>('/api/v1/trackers/mood?limit=7').then(setHistory).catch(() => {});
  }, [saved]);

  const submit = async () => {
    if (!selected) return;
    const emoji = MOOD_EMOJIS.find((m) => m.level === selected);
    await apiFetch('/api/v1/trackers/mood', {
      method: 'POST',
      body: JSON.stringify({ mood_level: selected, emoji: emoji?.emoji, note: note || null }),
    });
    setSaved(true);
    setNote('');
    setSelected(null);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">How are you feeling?</h2>

      {saved && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm">Mood logged! Keep it up.</div>}

      <div className="flex justify-center gap-4">
        {MOOD_EMOJIS.map((m) => (
          <button key={m.level} onClick={() => setSelected(m.level)}
            className={`text-4xl p-3 rounded-2xl transition ${selected === m.level ? 'bg-emerald-100 scale-110 shadow-md' : 'hover:bg-gray-50'}`}>
            <span>{m.emoji}</span>
            <div className="text-xs mt-1 text-gray-500">{m.label}</div>
          </button>
        ))}
      </div>

      <textarea value={note} onChange={(e) => setNote(e.target.value)}
        placeholder="Want to share more about how you're feeling? (optional)"
        className="w-full p-4 rounded-2xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition resize-none h-32" />

      <button onClick={submit} disabled={!selected}
        className="w-full py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition font-medium disabled:opacity-50">
        Log Mood
      </button>

      {history.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Recent Entries</h3>
          <div className="space-y-2">
            {history.map((h) => (
              <div key={h.id} className="bg-white p-3 rounded-xl border border-gray-100 flex justify-between items-center">
                <span className="text-2xl">{h.emoji || '😐'}</span>
                <span className="text-sm text-gray-500">{new Date(h.recorded_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

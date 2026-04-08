'use client';

import { useState } from 'react';
import { apiFetch } from '@/lib/api-client';

const ACTIVITIES = ['Exercise', 'Walking', 'Reading', 'Meditation', 'Yoga', 'Cooking', 'Gardening', 'Art', 'Music', 'Other'];

export default function ActivityTrackerPage() {
  const [type, setType] = useState('');
  const [duration, setDuration] = useState(30);
  const [saved, setSaved] = useState(false);

  const submit = async () => {
    if (!type) return;
    await apiFetch('/api/v1/trackers/activity', {
      method: 'POST',
      body: JSON.stringify({ activity_type: type, duration_minutes: duration, intensity: 3 }),
    });
    setSaved(true);
    setType('');
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Activity Log</h2>
      {saved && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm">Activity logged!</div>}

      <div className="grid grid-cols-2 gap-2">
        {ACTIVITIES.map((a) => (
          <button key={a} onClick={() => setType(a)}
            className={`p-3 rounded-xl text-sm transition ${type === a ? 'bg-emerald-600 text-white' : 'bg-white border border-gray-200 hover:border-emerald-300'}`}>
            {a}
          </button>
        ))}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-600 mb-2">Duration: {duration} min</label>
        <input type="range" min={5} max={180} step={5} value={duration} onChange={(e) => setDuration(parseInt(e.target.value))}
          className="w-full accent-emerald-600" />
      </div>

      <button onClick={submit} disabled={!type}
        className="w-full py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition font-medium disabled:opacity-50">
        Log Activity
      </button>
    </div>
  );
}

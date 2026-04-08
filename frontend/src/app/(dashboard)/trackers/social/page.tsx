'use client';

import { useState } from 'react';
import { apiFetch } from '@/lib/api-client';

export default function SocialTrackerPage() {
  const [count, setCount] = useState(3);
  const [quality, setQuality] = useState(3);
  const [isolation, setIsolation] = useState(3);
  const [saved, setSaved] = useState(false);

  const submit = async () => {
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1);
    await apiFetch('/api/v1/trackers/social', {
      method: 'POST',
      body: JSON.stringify({ interactions_count: count, quality_rating: quality, isolation_feeling: isolation, week_start: monday.toISOString().split('T')[0] }),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Social Check-in</h2>
      {saved && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm">Check-in saved!</div>}

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-6">
        <div>
          <label className="text-sm font-medium text-gray-600">Meaningful social interactions this week: {count}</label>
          <input type="range" min={0} max={20} value={count} onChange={(e) => setCount(parseInt(e.target.value))}
            className="w-full mt-2 accent-emerald-600" />
        </div>
        <div>
          <label className="text-sm font-medium text-gray-600">Quality of interactions: {quality}/5</label>
          <input type="range" min={1} max={5} value={quality} onChange={(e) => setQuality(parseInt(e.target.value))}
            className="w-full mt-2 accent-emerald-600" />
        </div>
        <div>
          <label className="text-sm font-medium text-gray-600">Feeling of isolation: {isolation}/5 (1=not at all, 5=very isolated)</label>
          <input type="range" min={1} max={5} value={isolation} onChange={(e) => setIsolation(parseInt(e.target.value))}
            className="w-full mt-2 accent-emerald-600" />
        </div>
      </div>

      <button onClick={submit}
        className="w-full py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition font-medium">
        Submit Check-in
      </button>
    </div>
  );
}

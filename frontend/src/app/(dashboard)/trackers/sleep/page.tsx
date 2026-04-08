'use client';

import { useState } from 'react';
import { apiFetch } from '@/lib/api-client';

export default function SleepTrackerPage() {
  const [duration, setDuration] = useState(7);
  const [quality, setQuality] = useState(3);
  const [saved, setSaved] = useState(false);

  const submit = async () => {
    await apiFetch('/api/v1/trackers/sleep', {
      method: 'POST',
      body: JSON.stringify({ sleep_duration: duration, sleep_quality: quality, disturbances: 0 }),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const qualityLabels = ['', 'Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'];

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Sleep Tracker</h2>
      {saved && <div className="p-3 bg-emerald-50 text-emerald-700 rounded-xl text-sm">Sleep logged!</div>}

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-3">
            Hours of Sleep: <span className="text-emerald-600 font-bold text-lg">{duration}h</span>
          </label>
          <input type="range" min={0} max={14} step={0.5} value={duration} onChange={(e) => setDuration(parseFloat(e.target.value))}
            className="w-full accent-emerald-600" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-600 mb-3">
            Quality: <span className="text-emerald-600 font-bold">{qualityLabels[quality]}</span>
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((v) => (
              <button key={v} onClick={() => setQuality(v)}
                className={`flex-1 py-3 rounded-xl text-sm transition ${quality === v ? 'bg-emerald-600 text-white' : 'bg-gray-100 hover:bg-gray-200'}`}>
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>

      <button onClick={submit}
        className="w-full py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition font-medium">
        Log Sleep
      </button>
    </div>
  );
}

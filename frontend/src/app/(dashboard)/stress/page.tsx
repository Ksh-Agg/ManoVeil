'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';
import { SCORE_CATEGORIES } from '@/lib/constants';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, Cell, ReferenceLine } from 'recharts';

interface StressScore {
  id: string;
  fused_score: number;
  psychometric_score: number;
  nlp_score: number;
  category: string;
  yellow_flag: boolean;
  shap_values: Record<string, number> | null;
  feature_values: Record<string, number> | null;
  computed_at: string;
}

interface SHAPExplanation {
  score_id: string;
  fused_score: number;
  category: string;
  feature_names: string[];
  feature_values: number[];
  shap_values: number[];
  base_value: number;
}

function getCategoryColor(category: string): string {
  const cat = SCORE_CATEGORIES[category as keyof typeof SCORE_CATEGORIES];
  return cat?.color || '#6b7280';
}

function getCategoryLabel(category: string): string {
  const cat = SCORE_CATEGORIES[category as keyof typeof SCORE_CATEGORIES];
  return cat?.label || category;
}

export default function StressPage() {
  const [current, setCurrent] = useState<StressScore | null>(null);
  const [history, setHistory] = useState<StressScore[]>([]);
  const [shap, setShap] = useState<SHAPExplanation | null>(null);
  const [computing, setComputing] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [score, hist] = await Promise.all([
        apiFetch<StressScore | null>('/api/v1/stress/current'),
        apiFetch<StressScore[]>('/api/v1/stress/history?days=30'),
      ]);
      setCurrent(score);
      setHistory(hist);
      if (score) {
        const explanation = await apiFetch<SHAPExplanation>(`/api/v1/stress/${score.id}/shap`).catch(() => null);
        setShap(explanation);
      }
    } catch {
      // ignore
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const compute = async () => {
    setComputing(true);
    try {
      const score = await apiFetch<StressScore>('/api/v1/stress/compute', { method: 'POST' });
      setCurrent(score);
      await load();
    } catch {
      // ignore
    }
    setComputing(false);
  };

  const gaugeAngle = current ? (current.fused_score / 10) * 180 : 0;

  const shapData = shap
    ? shap.feature_names.map((name, i) => ({
        name: name.replace(/_/g, ' '),
        value: shap.shap_values[i],
        feature_value: shap.feature_values[i],
      })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    : [];

  const historyData = [...history].reverse().map((s) => ({
    date: new Date(s.computed_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    score: s.fused_score,
    category: s.category,
  }));

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Stress Score Dashboard</h2>
        <button onClick={compute} disabled={computing}
          className="px-4 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition text-sm font-medium disabled:opacity-50">
          {computing ? 'Computing...' : 'Recompute Score'}
        </button>
      </div>

      {!current ? (
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center">
          <p className="text-gray-500 mb-4">No stress score computed yet. Take an assessment or log some tracker data first.</p>
          <button onClick={compute} disabled={computing}
            className="px-6 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition font-medium disabled:opacity-50">
            Compute My Score
          </button>
        </div>
      ) : (
        <>
          {/* Score Gauge */}
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex flex-col items-center">
              <svg viewBox="0 0 200 120" className="w-64 h-40">
                {/* Background arc */}
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#e5e7eb" strokeWidth="12" strokeLinecap="round" />
                {/* Score arc */}
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none"
                  stroke={getCategoryColor(current.category)} strokeWidth="12" strokeLinecap="round"
                  strokeDasharray={`${(gaugeAngle / 180) * 251.3} 251.3`} />
                {/* Score text */}
                <text x="100" y="85" textAnchor="middle" className="text-3xl font-bold" fill={getCategoryColor(current.category)} fontSize="28">
                  {current.fused_score.toFixed(1)}
                </text>
                <text x="100" y="105" textAnchor="middle" fill="#6b7280" fontSize="12">
                  {getCategoryLabel(current.category)}
                </text>
              </svg>

              {current.yellow_flag && (
                <div className="mt-2 px-3 py-1 bg-yellow-50 text-yellow-700 rounded-lg text-sm font-medium">
                  Yellow Flag — Score near tier boundary
                </div>
              )}

              <div className="flex gap-8 mt-4 text-sm text-gray-500">
                <div>Psychometric: <span className="font-semibold text-gray-700">{current.psychometric_score.toFixed(1)}</span></div>
                <div>NLP: <span className="font-semibold text-gray-700">{current.nlp_score.toFixed(1)}</span></div>
              </div>

              <p className="text-xs text-gray-400 mt-2">
                Fused = 60% psychometric + 40% NLP sentiment
              </p>
            </div>
          </div>

          {/* Score Legend */}
          <div className="flex flex-wrap gap-2 justify-center">
            {Object.values(SCORE_CATEGORIES).map((cat) => (
              <div key={cat.label} className="flex items-center gap-1.5 text-xs text-gray-500">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                <span>{cat.label} ({cat.range})</span>
              </div>
            ))}
          </div>

          {/* History Chart */}
          {historyData.length > 1 && (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">30-Day Trend</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={historyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}
                    formatter={(value: number) => [value.toFixed(1), 'Score']}
                  />
                  <ReferenceLine y={2} stroke="#22c55e" strokeDasharray="3 3" />
                  <ReferenceLine y={4.5} stroke="#84cc16" strokeDasharray="3 3" />
                  <ReferenceLine y={7} stroke="#f59e0b" strokeDasharray="3 3" />
                  <ReferenceLine y={8.9} stroke="#f97316" strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* SHAP Waterfall */}
          {shapData.length > 0 && (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">What's Contributing to Your Score</h3>
              <p className="text-xs text-gray-400 mb-4">SHAP feature contributions — positive values increase your stress score</p>
              <ResponsiveContainer width="100%" height={shapData.length * 40 + 20}>
                <BarChart data={shapData} layout="vertical" margin={{ left: 100, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} stroke="#9ca3af" width={90} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb' }}
                    formatter={(value: number) => [value.toFixed(3), 'SHAP value']}
                  />
                  <ReferenceLine x={0} stroke="#9ca3af" />
                  <Bar dataKey="value" radius={[4, 4, 4, 4]}>
                    {shapData.map((entry, i) => (
                      <Cell key={i} fill={entry.value > 0 ? '#ef4444' : '#22c55e'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
    </div>
  );
}

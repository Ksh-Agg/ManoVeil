'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

interface PlatformStats {
  total_users: number;
  total_assessments: number;
  total_chat_sessions: number;
  avg_score_by_age_group: Record<string, number>;
  category_distribution: Record<string, number>;
}

const CATEGORY_COLORS: Record<string, string> = {
  minimal: '#22c55e',
  mild: '#84cc16',
  moderate: '#f59e0b',
  moderately_severe: '#f97316',
  severe: '#ef4444',
};

export default function AnalyticsPage() {
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<PlatformStats>('/api/v1/clinical/analytics')
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  const ageData = Object.entries(stats.avg_score_by_age_group).map(([group, score]) => ({
    name: group.replace(/_/g, ' '),
    score: Number(score.toFixed(1)),
  }));

  const categoryData = Object.entries(stats.category_distribution).map(([cat, count]) => ({
    name: cat.replace(/_/g, ' '),
    value: count,
    color: CATEGORY_COLORS[cat] || '#6b7280',
  }));

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Platform Analytics</h2>

      {/* Overview Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-teal-600">{stats.total_users}</p>
          <p className="text-sm text-gray-500 mt-1">Total Users</p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-blue-600">{stats.total_assessments}</p>
          <p className="text-sm text-gray-500 mt-1">Assessments Taken</p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-purple-600">{stats.total_chat_sessions}</p>
          <p className="text-sm text-gray-500 mt-1">Chat Sessions</p>
        </div>
      </div>

      {/* Avg Score by Age Group */}
      {ageData.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Average Stress Score by Age Group</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ageData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#9ca3af" />
              <YAxis domain={[0, 10]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb' }} />
              <Bar dataKey="score" fill="#14b8a6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Category Distribution */}
      {categoryData.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Score Category Distribution</h3>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width="50%" height={250}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} innerRadius={50}>
                  {categoryData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {categoryData.map((cat) => (
                <div key={cat.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: cat.color }} />
                  <span className="text-sm text-gray-600 capitalize">{cat.name}: {cat.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

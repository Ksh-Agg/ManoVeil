'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api-client';
import { useAuthStore } from '@/stores/auth-store';
import { PERSONAS, SCORE_CATEGORIES } from '@/lib/constants';

export default function DashboardHome() {
  const { user } = useAuthStore();
  const [score, setScore] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    apiFetch('/api/v1/stress/current').then(setScore).catch(() => {});
    apiFetch('/api/v1/trackers/summary').then(setSummary).catch(() => {});
  }, []);

  const persona = user?.persona as keyof typeof PERSONAS || 'manoveil_core';
  const personaInfo = PERSONAS[persona] || PERSONAS.manoveil_core;
  const scoreInfo = score ? SCORE_CATEGORIES[score.category as keyof typeof SCORE_CATEGORIES] : null;

  return (
    <div className="space-y-8">
      {/* Welcome */}
      <div className="rounded-3xl p-8 shadow-sm" style={{ backgroundColor: personaInfo.bg }}>
        <h1 className="text-3xl font-bold" style={{ color: personaInfo.text }}>
          Welcome back, {user?.full_name?.split(' ')[0]}
        </h1>
        <p className="mt-2 opacity-75" style={{ color: personaInfo.text }}>
          {personaInfo.description}. How are you feeling today?
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { href: '/dashboard/chat', label: 'Talk to Me', icon: '💬', color: 'bg-blue-50 text-blue-800' },
          { href: '/dashboard/trackers/mood', label: 'Log Mood', icon: '😊', color: 'bg-amber-50 text-amber-800' },
          { href: '/dashboard/assessments', label: 'Assessment', icon: '📋', color: 'bg-green-50 text-green-800' },
          { href: '/dashboard/interventions', label: 'Wellness', icon: '🧘', color: 'bg-purple-50 text-purple-800' },
        ].map((a) => (
          <Link key={a.href} href={a.href}
            className={`p-6 rounded-2xl ${a.color} text-center card-hover border border-transparent hover:border-gray-200`}>
            <div className="text-3xl mb-2">{a.icon}</div>
            <div className="font-medium text-sm">{a.label}</div>
          </Link>
        ))}
      </div>

      {/* Score Widget */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Stress Score</h3>
          {score ? (
            <div className="text-center">
              <div className="text-5xl font-bold mb-2" style={{ color: scoreInfo?.color }}>
                {score.fused_score.toFixed(1)}
              </div>
              <div className="text-sm font-medium" style={{ color: scoreInfo?.color }}>
                {scoreInfo?.label}
              </div>
              <div className="mt-4 w-full bg-gray-100 rounded-full h-3">
                <div className="h-3 rounded-full transition-all duration-500" style={{ width: `${score.fused_score * 10}%`, backgroundColor: scoreInfo?.color }} />
              </div>
              {score.yellow_flag && (
                <div className="mt-3 text-xs text-amber-600 bg-amber-50 px-3 py-1 rounded-full inline-block">
                  Yellow Flag — near tier boundary
                </div>
              )}
            </div>
          ) : (
            <div className="text-center text-gray-400 py-8">
              <p>No score yet</p>
              <Link href="/dashboard/assessments" className="text-emerald-600 text-sm hover:underline mt-2 inline-block">
                Take an assessment to get started
              </Link>
            </div>
          )}
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Weekly Summary</h3>
          {summary ? (
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="text-gray-500">Mood Trend</span><span className="font-medium capitalize">{summary.mood_trend}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Sleep Quality (avg)</span><span className="font-medium">{summary.avg_sleep_quality_7d?.toFixed(1) || '—'}/5</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Sleep Duration (avg)</span><span className="font-medium">{summary.avg_sleep_duration_7d?.toFixed(1) || '—'}h</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Activities</span><span className="font-medium">{summary.total_activities_7d}</span></div>
              <div className="flex justify-between"><span className="text-gray-500">Social Quality</span><span className="font-medium">{summary.avg_social_quality_7d?.toFixed(1) || '—'}/5</span></div>
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">Start tracking to see your summary</p>
          )}
        </div>
      </div>
    </div>
  );
}

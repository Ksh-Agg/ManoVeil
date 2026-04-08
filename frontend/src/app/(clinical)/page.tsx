'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api-client';

interface PatientSummary {
  user: { id: string; full_name: string; email: string; age_group: string; persona: string };
  latest_score: number | null;
  latest_category: string | null;
  score_trend: string | null;
  crisis_count: number;
  notes_count: number;
}

interface Alert {
  patient: { id: string; full_name: string };
  alert_type: string;
  severity: string;
  message: string;
  created_at: string;
}

export default function ClinicalHomePage() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<PatientSummary[]>('/api/v1/clinical/patients'),
      apiFetch<Alert[]>('/api/v1/clinical/alerts'),
    ]).then(([p, a]) => {
      setPatients(p);
      setAlerts(a);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const atRisk = patients.filter((p) => p.latest_category === 'severe' || p.latest_category === 'moderately_severe');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Clinical Dashboard</h2>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-teal-600">{patients.length}</p>
          <p className="text-sm text-gray-500 mt-1">Total Patients</p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-red-500">{atRisk.length}</p>
          <p className="text-sm text-gray-500 mt-1">At Risk</p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-amber-500">{alerts.length}</p>
          <p className="text-sm text-gray-500 mt-1">Active Alerts</p>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 text-center">
          <p className="text-3xl font-bold text-blue-500">{patients.filter((p) => p.score_trend === 'improving').length}</p>
          <p className="text-sm text-gray-500 mt-1">Improving</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        <Link href="/clinical/patients" className="bg-teal-50 rounded-2xl p-5 hover:bg-teal-100 transition">
          <p className="text-2xl mb-2">👥</p>
          <h3 className="font-semibold text-teal-800">View Patients</h3>
          <p className="text-sm text-teal-600 mt-1">Manage your patient list</p>
        </Link>
        <Link href="/clinical/alerts" className="bg-red-50 rounded-2xl p-5 hover:bg-red-100 transition">
          <p className="text-2xl mb-2">🔔</p>
          <h3 className="font-semibold text-red-800">Check Alerts</h3>
          <p className="text-sm text-red-600 mt-1">{alerts.length} alerts need attention</p>
        </Link>
        <Link href="/clinical/analytics" className="bg-blue-50 rounded-2xl p-5 hover:bg-blue-100 transition">
          <p className="text-2xl mb-2">📊</p>
          <h3 className="font-semibold text-blue-800">Analytics</h3>
          <p className="text-sm text-blue-600 mt-1">Platform-wide insights</p>
        </Link>
      </div>

      {/* Recent Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Recent Alerts</h3>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((a, i) => (
              <div key={i} className={`p-3 rounded-xl flex items-center justify-between ${
                a.severity === 'red' || a.severity === 'sos' ? 'bg-red-50' : a.severity === 'orange' ? 'bg-orange-50' : 'bg-yellow-50'
              }`}>
                <div>
                  <p className="font-medium text-gray-800">{a.patient.full_name}</p>
                  <p className="text-sm text-gray-600">{a.message}</p>
                </div>
                <span className="text-xs text-gray-400">{new Date(a.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

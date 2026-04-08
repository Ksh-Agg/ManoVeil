'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api-client';
import { SCORE_CATEGORIES } from '@/lib/constants';

interface PatientSummary {
  user: { id: string; full_name: string; email: string; age_group: string; persona: string };
  latest_score: number | null;
  latest_category: string | null;
  score_trend: string | null;
  last_active: string | null;
  crisis_count: number;
  notes_count: number;
}

export default function PatientsPage() {
  const [patients, setPatients] = useState<PatientSummary[]>([]);
  const [search, setSearch] = useState('');
  const [linkEmail, setLinkEmail] = useState('');
  const [linking, setLinking] = useState(false);
  const [linkError, setLinkError] = useState('');
  const [showLink, setShowLink] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const p = await apiFetch<PatientSummary[]>('/api/v1/clinical/patients').catch(() => []);
    setPatients(p);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const linkPatient = async () => {
    setLinking(true);
    setLinkError('');
    try {
      // The API expects patient_id, but we search by email first
      // For now we pass the UUID directly — in production you'd resolve email→id
      await apiFetch('/api/v1/clinical/patients/link', {
        method: 'POST',
        body: JSON.stringify({ patient_id: linkEmail, is_primary: true }),
      });
      setLinkEmail('');
      setShowLink(false);
      await load();
    } catch (e: any) {
      setLinkError(e.message || 'Failed to link patient');
    }
    setLinking(false);
  };

  const filtered = patients.filter((p) =>
    p.user.full_name.toLowerCase().includes(search.toLowerCase()) ||
    p.user.email.toLowerCase().includes(search.toLowerCase())
  );

  const trendIcon = (trend: string | null) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-800">Patients</h2>
        <button onClick={() => setShowLink(!showLink)}
          className="px-4 py-2 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition text-sm font-medium">
          + Link Patient
        </button>
      </div>

      {showLink && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 space-y-3">
          <p className="text-sm text-gray-600">Enter the patient&apos;s user ID to link them to your account:</p>
          <input value={linkEmail} onChange={(e) => setLinkEmail(e.target.value)}
            placeholder="Patient User ID (UUID)"
            className="w-full p-3 rounded-xl border border-gray-200 focus:border-teal-400 focus:ring-2 focus:ring-teal-100 outline-none transition text-sm" />
          {linkError && <p className="text-sm text-red-500">{linkError}</p>}
          <button onClick={linkPatient} disabled={linking || !linkEmail}
            className="px-4 py-2 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition text-sm disabled:opacity-50">
            {linking ? 'Linking...' : 'Link'}
          </button>
        </div>
      )}

      <input value={search} onChange={(e) => setSearch(e.target.value)}
        placeholder="Search patients..."
        className="w-full p-3 rounded-xl border border-gray-200 focus:border-teal-400 focus:ring-2 focus:ring-teal-100 outline-none transition" />

      {filtered.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center text-gray-500">
          {patients.length === 0 ? 'No patients linked yet. Link a patient to get started.' : 'No patients match your search.'}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((p) => {
            const cat = p.latest_category ? SCORE_CATEGORIES[p.latest_category as keyof typeof SCORE_CATEGORIES] : null;
            return (
              <Link key={p.user.id} href={`/clinical/patients/${p.user.id}`}
                className="block bg-white rounded-2xl p-5 shadow-sm border border-gray-100 hover:border-teal-200 transition">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-800">{p.user.full_name}</h3>
                    <p className="text-sm text-gray-500">{p.user.email} · {p.user.age_group.replace(/_/g, ' ')}</p>
                  </div>
                  <div className="flex items-center gap-3 text-right">
                    {p.latest_score !== null && (
                      <div>
                        <p className="text-lg font-bold" style={{ color: cat?.color || '#6b7280' }}>
                          {p.latest_score.toFixed(1)}
                        </p>
                        <p className="text-xs text-gray-400">{cat?.label || 'N/A'}</p>
                      </div>
                    )}
                    <span className="text-xl">{trendIcon(p.score_trend)}</span>
                  </div>
                </div>
                <div className="flex gap-4 mt-3 text-xs text-gray-400">
                  <span>Crisis events: {p.crisis_count}</span>
                  <span>Notes: {p.notes_count}</span>
                  {p.last_active && <span>Last active: {new Date(p.last_active).toLocaleDateString()}</span>}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

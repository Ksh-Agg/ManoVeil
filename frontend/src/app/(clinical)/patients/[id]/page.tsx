'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { apiFetch } from '@/lib/api-client';
import { SCORE_CATEGORIES } from '@/lib/constants';

interface TimelineEntry {
  type: string;
  date: string;
  [key: string]: any;
}

interface AISummary {
  patient_id: string;
  summary: string;
  key_observations: string[];
  recommendations: string[];
  risk_level: string;
  generated_at: string;
}

interface Note {
  id: string;
  content: string;
  note_type: string;
  therapist_name: string | null;
  created_at: string;
}

export default function PatientDetailPage() {
  const params = useParams();
  const patientId = params.id as string;
  const [timeline, setTimeline] = useState<any>(null);
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [notes, setNotes] = useState<Note[]>([]);
  const [noteContent, setNoteContent] = useState('');
  const [noteType, setNoteType] = useState('session_note');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'timeline' | 'summary' | 'notes'>('timeline');

  useEffect(() => {
    Promise.all([
      apiFetch(`/api/v1/clinical/patients/${patientId}/timeline`),
      apiFetch<AISummary>(`/api/v1/clinical/patients/${patientId}/summary`).catch(() => null),
      apiFetch<Note[]>(`/api/v1/clinical/notes?patient_id=${patientId}`).catch(() => []),
    ]).then(([tl, sum, n]) => {
      setTimeline(tl);
      setSummary(sum);
      setNotes(n);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [patientId]);

  const addNote = async () => {
    if (!noteContent.trim()) return;
    setSaving(true);
    try {
      await apiFetch('/api/v1/clinical/notes', {
        method: 'POST',
        body: JSON.stringify({ patient_id: patientId, content: noteContent, note_type: noteType }),
      });
      const n = await apiFetch<Note[]>(`/api/v1/clinical/notes?patient_id=${patientId}`);
      setNotes(n);
      setNoteContent('');
    } catch {
      // ignore
    }
    setSaving(false);
  };

  const buildTimeline = (): TimelineEntry[] => {
    if (!timeline) return [];
    const entries: TimelineEntry[] = [];

    if (timeline.assessments) {
      timeline.assessments.forEach((a: any) => entries.push({ type: 'assessment', date: a.created_at, ...a }));
    }
    if (timeline.stress_scores) {
      timeline.stress_scores.forEach((s: any) => entries.push({ type: 'stress', date: s.computed_at, ...s }));
    }
    if (timeline.mood_entries) {
      timeline.mood_entries.forEach((m: any) => entries.push({ type: 'mood', date: m.recorded_at, ...m }));
    }
    if (timeline.crisis_events) {
      timeline.crisis_events.forEach((c: any) => entries.push({ type: 'crisis', date: c.created_at, ...c }));
    }
    if (timeline.notes) {
      timeline.notes.forEach((n: any) => entries.push({ type: 'note', date: n.created_at, ...n }));
    }

    return entries.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  };

  const riskColor = (level: string) => {
    if (level === 'high') return 'text-red-600 bg-red-50';
    if (level === 'moderate') return 'text-amber-600 bg-amber-50';
    return 'text-green-600 bg-green-50';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  const entries = buildTimeline();
  const patient = timeline?.patient;

  return (
    <div className="space-y-6">
      {/* Patient Header */}
      {patient && (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-800">{patient.full_name}</h2>
          <p className="text-gray-500">{patient.email} · {patient.age_group?.replace(/_/g, ' ')}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2">
        {(['timeline', 'summary', 'notes'] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition ${tab === t ? 'bg-teal-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'}`}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Timeline Tab */}
      {tab === 'timeline' && (
        <div className="space-y-3">
          {entries.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No timeline data yet.</p>
          ) : (
            entries.map((entry, i) => (
              <div key={i} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-start gap-3">
                <span className="text-xl">
                  {entry.type === 'assessment' ? '📋' : entry.type === 'stress' ? '🎯' : entry.type === 'mood' ? (entry.emoji || '😐') : entry.type === 'crisis' ? '🚨' : '📝'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-gray-800 capitalize">{entry.type.replace('_', ' ')}</p>
                    <span className="text-xs text-gray-400">{new Date(entry.date).toLocaleString()}</span>
                  </div>
                  {entry.type === 'assessment' && (
                    <p className="text-sm text-gray-600">
                      {entry.assessment_type}: Score {entry.normalized_score?.toFixed(1)} — {entry.category}
                    </p>
                  )}
                  {entry.type === 'stress' && (
                    <p className="text-sm text-gray-600">
                      Fused: {entry.fused_score?.toFixed(1)} (Psych: {entry.psychometric_score?.toFixed(1)}, NLP: {entry.nlp_score?.toFixed(1)}) — {entry.category}
                    </p>
                  )}
                  {entry.type === 'mood' && (
                    <p className="text-sm text-gray-600">{entry.mood_level}{entry.note ? ` — "${entry.note}"` : ''}</p>
                  )}
                  {entry.type === 'crisis' && (
                    <p className="text-sm text-red-600">Severity: {entry.severity} — {entry.action_taken || 'Logged'}</p>
                  )}
                  {entry.type === 'note' && (
                    <p className="text-sm text-gray-600">{entry.content?.slice(0, 200)}</p>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Summary Tab */}
      {tab === 'summary' && (
        <div className="space-y-4">
          {summary ? (
            <>
              <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-700">AI-Generated Summary</h3>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${riskColor(summary.risk_level)}`}>
                    {summary.risk_level.toUpperCase()} RISK
                  </span>
                </div>
                <p className="text-gray-600">{summary.summary}</p>
              </div>

              {summary.key_observations.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                  <h4 className="font-semibold text-gray-700 mb-3">Key Observations</h4>
                  <ul className="space-y-2">
                    {summary.key_observations.map((obs, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="text-teal-500 mt-0.5">•</span>
                        <span>{obs}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {summary.recommendations.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
                  <h4 className="font-semibold text-gray-700 mb-3">Recommendations</h4>
                  <ul className="space-y-2">
                    {summary.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="text-blue-500 mt-0.5">→</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <p className="text-xs text-gray-400 text-right">
                Generated {new Date(summary.generated_at).toLocaleString()}
              </p>
            </>
          ) : (
            <p className="text-gray-500 text-center py-8">No summary available. The patient needs more data for an AI summary.</p>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {tab === 'notes' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 space-y-3">
            <h3 className="font-semibold text-gray-700">Add Note</h3>
            <select value={noteType} onChange={(e) => setNoteType(e.target.value)}
              className="w-full p-2.5 rounded-xl border border-gray-200 text-sm">
              <option value="session_note">Session Note</option>
              <option value="observation">Observation</option>
              <option value="treatment_plan">Treatment Plan</option>
              <option value="follow_up">Follow-up</option>
            </select>
            <textarea value={noteContent} onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Write your clinical note..."
              className="w-full p-3 rounded-xl border border-gray-200 focus:border-teal-400 focus:ring-2 focus:ring-teal-100 outline-none transition resize-none h-32 text-sm" />
            <button onClick={addNote} disabled={saving || !noteContent.trim()}
              className="px-4 py-2 bg-teal-600 text-white rounded-xl hover:bg-teal-700 transition text-sm font-medium disabled:opacity-50">
              {saving ? 'Saving...' : 'Save Note'}
            </button>
          </div>

          {notes.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No notes yet.</p>
          ) : (
            notes.map((n) => (
              <div key={n.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
                    {n.note_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs text-gray-400">{new Date(n.created_at).toLocaleString()}</span>
                </div>
                <p className="text-sm text-gray-700">{n.content}</p>
                {n.therapist_name && <p className="text-xs text-gray-400 mt-2">— {n.therapist_name}</p>}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

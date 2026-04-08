'use client';

import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api-client';

interface Intervention {
  id: string;
  title: string;
  intervention_type: string;
  content: { description?: string; steps?: string[]; duration?: string; benefits?: string[] } | null;
  target_personas: string[];
  target_categories: string[];
}

interface Completion {
  id: string;
  intervention_id: string;
  feedback_rating: number | null;
  completed_at: string;
}

const TYPE_STYLES: Record<string, { bg: string; text: string; icon: string }> = {
  cbt: { bg: 'bg-blue-50', text: 'text-blue-700', icon: '🧠' },
  mindfulness: { bg: 'bg-purple-50', text: 'text-purple-700', icon: '🧘' },
  psychoeducation: { bg: 'bg-amber-50', text: 'text-amber-700', icon: '📚' },
};

export default function InterventionsPage() {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [completions, setCompletions] = useState<Completion[]>([]);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [completing, setCompleting] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<Intervention[]>('/api/v1/interventions'),
      apiFetch<Completion[]>('/api/v1/interventions/history/completions'),
    ]).then(([ints, comps]) => {
      setInterventions(ints);
      setCompletions(comps);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const complete = async (id: string, rating: number) => {
    setCompleting(id);
    try {
      await apiFetch(`/api/v1/interventions/${id}/complete`, {
        method: 'POST',
        body: JSON.stringify({ feedback_rating: rating }),
      });
      const comps = await apiFetch<Completion[]>('/api/v1/interventions/history/completions');
      setCompletions(comps);
    } catch {
      // ignore
    }
    setCompleting(null);
  };

  const isCompleted = (id: string) => completions.some((c) => c.intervention_id === id);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800">Wellness Interventions</h2>
      <p className="text-gray-500">Personalized activities recommended based on your assessment results and stress profile.</p>

      {interventions.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 text-center text-gray-500">
          No interventions available yet. Complete an assessment to get personalized recommendations.
        </div>
      ) : (
        <div className="space-y-4">
          {interventions.map((int) => {
            const style = TYPE_STYLES[int.intervention_type] || TYPE_STYLES.cbt;
            const done = isCompleted(int.id);
            const isExpanded = expanded === int.id;

            return (
              <div key={int.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <button onClick={() => setExpanded(isExpanded ? null : int.id)}
                  className="w-full p-5 flex items-center gap-4 text-left hover:bg-gray-50 transition">
                  <span className="text-3xl">{style.icon}</span>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-800">{int.title}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
                        {int.intervention_type.toUpperCase()}
                      </span>
                      {done && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">Completed</span>
                      )}
                    </div>
                  </div>
                  <span className="text-gray-400 text-xl">{isExpanded ? '−' : '+'}</span>
                </button>

                {isExpanded && int.content && (
                  <div className="px-5 pb-5 space-y-4 border-t border-gray-100 pt-4">
                    {int.content.description && (
                      <p className="text-gray-600 text-sm">{int.content.description}</p>
                    )}
                    {int.content.duration && (
                      <p className="text-xs text-gray-400">Duration: {int.content.duration}</p>
                    )}
                    {int.content.steps && int.content.steps.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Steps</h4>
                        <ol className="list-decimal list-inside space-y-1.5">
                          {int.content.steps.map((step, i) => (
                            <li key={i} className="text-sm text-gray-600">{step}</li>
                          ))}
                        </ol>
                      </div>
                    )}
                    {int.content.benefits && int.content.benefits.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Benefits</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {int.content.benefits.map((b, i) => (
                            <li key={i} className="text-sm text-gray-600">{b}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {!done && (
                      <div>
                        <p className="text-sm text-gray-500 mb-2">Rate this activity after completing it:</p>
                        <div className="flex gap-2">
                          {[1, 2, 3, 4, 5].map((r) => (
                            <button key={r} onClick={() => complete(int.id, r)} disabled={completing === int.id}
                              className="flex-1 py-2 rounded-xl text-sm transition bg-gray-100 hover:bg-emerald-100 hover:text-emerald-700 disabled:opacity-50">
                              {'⭐'.repeat(r)}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

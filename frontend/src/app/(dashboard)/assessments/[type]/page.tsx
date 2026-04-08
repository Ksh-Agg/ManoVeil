'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api-client';
import { SCORE_CATEGORIES } from '@/lib/constants';

export default function AssessmentFormPage() {
  const { type } = useParams();
  const router = useRouter();
  const [instrument, setInstrument] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [current, setCurrent] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch<any>(`/api/v1/assessments/instruments/${type}/questions`)
      .then(setInstrument).catch(() => {});
  }, [type]);

  if (!instrument) return <div className="text-center py-20 text-gray-400">Loading assessment...</div>;

  const questions = instrument.questions || [];
  const q = questions[current];
  const progress = ((current + (result ? 1 : 0)) / questions.length) * 100;

  const submit = async () => {
    setLoading(true);
    try {
      const res = await apiFetch<any>('/api/v1/assessments/', {
        method: 'POST',
        body: JSON.stringify({ assessment_type: type, raw_responses: answers }),
      });
      setResult(res);
      // Also compute stress score
      await apiFetch('/api/v1/stress/compute', { method: 'POST' }).catch(() => {});
    } catch (err) {
      alert('Failed to submit assessment');
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    const catInfo = SCORE_CATEGORIES[result.category as keyof typeof SCORE_CATEGORIES];
    return (
      <div className="max-w-lg mx-auto text-center space-y-6 py-12">
        <h2 className="text-2xl font-bold text-gray-800">Assessment Complete</h2>
        <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100">
          <div className="text-6xl font-bold mb-3" style={{ color: catInfo?.color }}>{result.normalized_score.toFixed(1)}</div>
          <div className="text-lg font-medium" style={{ color: catInfo?.color }}>{catInfo?.label}</div>
          <div className="mt-4 w-full bg-gray-100 rounded-full h-3">
            <div className="h-3 rounded-full" style={{ width: `${result.normalized_score * 10}%`, backgroundColor: catInfo?.color }} />
          </div>
        </div>
        <button onClick={() => router.push('/dashboard/stress')}
          className="px-8 py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition">
          View Stress Dashboard
        </button>
      </div>
    );
  }

  if (!q) return null;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-800">{instrument.name}</h2>
        <p className="text-sm text-gray-500 mt-1">Question {current + 1} of {questions.length}</p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div className="h-2 rounded-full bg-emerald-500 transition-all duration-300" style={{ width: `${progress}%` }} />
      </div>

      {/* Question */}
      <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <p className="text-lg text-gray-800 mb-6">{q.text}</p>
        <div className="space-y-3">
          {q.options.map((opt: any) => (
            <button key={opt.value}
              onClick={() => {
                setAnswers({ ...answers, [q.id]: opt.value });
                if (current < questions.length - 1) {
                  setTimeout(() => setCurrent(current + 1), 200);
                }
              }}
              className={`w-full text-left p-4 rounded-xl border-2 transition ${
                answers[q.id] === opt.value
                  ? 'border-emerald-500 bg-emerald-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}>
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button onClick={() => setCurrent(Math.max(0, current - 1))} disabled={current === 0}
          className="px-6 py-2 text-gray-500 hover:text-gray-800 disabled:opacity-30">
          Back
        </button>
        {current === questions.length - 1 && Object.keys(answers).length === questions.length && (
          <button onClick={submit} disabled={loading}
            className="px-8 py-3 bg-emerald-600 text-white rounded-2xl hover:bg-emerald-700 transition disabled:opacity-50">
            {loading ? 'Submitting...' : 'Submit Assessment'}
          </button>
        )}
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api-client';

export default function AssessmentsPage() {
  const [instruments, setInstruments] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    apiFetch<any[]>('/api/v1/assessments/instruments').then(setInstruments).catch(() => {});
    apiFetch<any[]>('/api/v1/assessments/?limit=10').then(setHistory).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-gray-800">Assessments</h2>

      <div>
        <h3 className="text-lg font-semibold text-gray-700 mb-4">Available for You</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {instruments.map((inst) => (
            <Link key={inst.type} href={`/dashboard/assessments/${inst.type}`}
              className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm card-hover">
              <h4 className="font-semibold text-gray-800">{inst.name}</h4>
              <p className="text-sm text-gray-500 mt-1">{inst.description}</p>
              <div className="flex gap-4 mt-3 text-xs text-gray-400">
                <span>{inst.question_count} questions</span>
                <span>~{inst.estimated_minutes} min</span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {history.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Completed</h3>
          <div className="space-y-2">
            {history.map((a) => (
              <div key={a.id} className="bg-white p-4 rounded-xl border border-gray-100 flex justify-between items-center">
                <div>
                  <span className="font-medium text-gray-800">{a.assessment_type.replace('_', '-').toUpperCase()}</span>
                  <span className="text-sm text-gray-400 ml-3">{new Date(a.completed_at).toLocaleDateString()}</span>
                </div>
                <div className="text-right">
                  <span className="font-semibold text-lg">{a.normalized_score.toFixed(1)}</span>
                  <span className="text-sm text-gray-500 ml-1">/10</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { apiFetch } from '@/lib/api-client';

interface Alert {
  patient: { id: string; full_name: string; email: string };
  alert_type: string;
  severity: string;
  message: string;
  created_at: string;
}

const SEVERITY_STYLES: Record<string, { bg: string; text: string; icon: string }> = {
  sos: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', icon: '🆘' },
  red: { bg: 'bg-red-50 border-red-200', text: 'text-red-700', icon: '🔴' },
  orange: { bg: 'bg-orange-50 border-orange-200', text: 'text-orange-700', icon: '🟠' },
  yellow_flag: { bg: 'bg-yellow-50 border-yellow-200', text: 'text-yellow-700', icon: '🟡' },
  info: { bg: 'bg-blue-50 border-blue-200', text: 'text-blue-700', icon: '🔵' },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    apiFetch<Alert[]>('/api/v1/clinical/alerts')
      .then(setAlerts)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === 'all' ? alerts : alerts.filter((a) => a.severity === filter || a.alert_type === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Alerts</h2>

      <div className="flex gap-2 flex-wrap">
        {['all', 'sos', 'red', 'orange', 'yellow_flag'].map((f) => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-sm transition ${filter === f ? 'bg-teal-600 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
            {f === 'all' ? 'All' : f === 'yellow_flag' ? 'Yellow Flag' : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="bg-white rounded-2xl p-8 text-center text-gray-500">
          No alerts to display.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((alert, i) => {
            const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.info;
            return (
              <div key={i} className={`rounded-2xl p-5 border ${style.bg} transition`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{style.icon}</span>
                    <div>
                      <Link href={`/clinical/patients/${alert.patient.id}`}
                        className={`font-semibold hover:underline ${style.text}`}>
                        {alert.patient.full_name}
                      </Link>
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      <div className="flex gap-3 mt-2 text-xs text-gray-400">
                        <span>{alert.alert_type.replace(/_/g, ' ')}</span>
                        <span>{alert.patient.email}</span>
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {new Date(alert.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api-client';
import { useAuthStore } from '@/stores/auth-store';
import { AGE_GROUPS } from '@/lib/constants';

export default function RegisterPage() {
  const [form, setForm] = useState({ email: '', password: '', full_name: '', date_of_birth: '', age_group: '', role: 'user' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiFetch<any>('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      login(data);
      router.push(form.role === 'therapist' ? '/clinical' : '/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur rounded-3xl shadow-lg p-8 border border-gray-100">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Create Your Space</h2>
      {error && <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm">{error}</div>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Full Name</label>
          <input type="text" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Password</label>
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={8}
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-1">Date of Birth</label>
          <input type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} required
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-600 mb-2">I am a...</label>
          <div className="grid grid-cols-2 gap-2">
            {AGE_GROUPS.map((ag) => (
              <button key={ag.value} type="button"
                onClick={() => setForm({ ...form, age_group: ag.value })}
                className={`p-3 rounded-xl border-2 text-sm transition ${form.age_group === ag.value ? 'border-emerald-500 bg-emerald-50 text-emerald-800' : 'border-gray-200 hover:border-gray-300'}`}>
                {ag.label}
              </button>
            ))}
            <button type="button"
              onClick={() => setForm({ ...form, role: 'therapist', age_group: form.age_group || 'adults_25_59' })}
              className={`p-3 rounded-xl border-2 text-sm transition ${form.role === 'therapist' ? 'border-teal-500 bg-teal-50 text-teal-800' : 'border-gray-200 hover:border-gray-300'}`}>
              Therapist / Doctor
            </button>
          </div>
        </div>
        <button type="submit" disabled={loading || !form.age_group}
          className="w-full py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition font-medium disabled:opacity-50">
          {loading ? 'Creating your space...' : 'Begin Your Journey'}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account? <Link href="/login" className="text-emerald-600 hover:underline">Sign in</Link>
      </p>
    </div>
  );
}
